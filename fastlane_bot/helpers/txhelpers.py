"""
Transaction handlers for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__ = "01/May/2023"

import asyncio
import nest_asyncio
from _decimal import Decimal

from json import loads
from dataclasses import dataclass
from typing import List, Any, Dict

import requests
from alchemy import Network, Alchemy
from web3.exceptions import TimeExhausted

from fastlane_bot.config import Config
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.utils import num_format, log_format, int_prefix

nest_asyncio.apply()

MAX_UINT256 = 2 ** 256 - 1
ETH_DECIMALS = 10 ** 18

@dataclass
class TxHelpers:
    """
    This class is used to organize web3 transaction tools.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    ConfigObj: Config

    def __post_init__(self):
        self.arb_contract = self.ConfigObj.BANCOR_ARBITRAGE_CONTRACT
        self.use_tenderly = self.ConfigObj.network.DEFAULT_PROVIDER == "tenderly"
        self.use_eip_1559 = self.ConfigObj.NETWORK in ["ethereum", "coinbase_base"]
        self.access_lists = self.ConfigObj.NETWORK in ["ethereum"]
        self.eth = self.ConfigObj.w3.eth

        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            self.wallet_address = self.ConfigObj.BINANCE14_WALLET_ADDRESS
        else:
            self.wallet_address = str(self.eth.account.from_key(self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL).address)

        if self.use_tenderly:
            self.alchemy = None
        else:
            self.alchemy = Alchemy(api_key=self.ConfigObj.WEB3_ALCHEMY_PROJECT_ID, network=Network.ETH_MAINNET, max_retries=3)

    def validate_and_submit_transaction(
        self,
        route_struct: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        expected_profit_gastkn: Decimal,
        expected_profit_usd: Decimal,
        log_object: Dict[str, Any],
        flashloan_struct: List[Dict]
    ) -> str:
        """
        Validates and submits a transaction to the arb contract.
        """

        self.ConfigObj.logger.info("[helpers.txhelpers.validate_and_submit_transaction] Validating trade...")
        self.ConfigObj.logger.debug(
            f"[helpers.txhelpers.validate_and_submit_transaction]:\n"
            f"- Routes: {route_struct}\n"
            f"- Source amount: {src_amt}\n"
            f"- Source token: {src_address}\n"
            f"- Expected profit: {num_format(expected_profit_gastkn)} GAS token ({num_format(expected_profit_usd)} USD)\n"
        )

        if self.ConfigObj.SELF_FUND:
            function = self.arb_contract.functions.fundAndArb(route_struct, src_address, src_amt)
            value = src_amt if src_address == self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS else 0
        elif flashloan_struct is None:
            function = self.arb_contract.functions.flashloanAndArb(route_struct, src_address, src_amt)
            value = 0
        else:
            function = self.arb_contract.functions.flashloanAndArbV2(flashloan_struct, route_struct)
            value = 0

        tx, current_gas_price, block_number = self._build_transaction(function=function, value=value)
        if tx is None:
            return None

        try:
            estimated_gas = self.eth.estimate_gas(transaction=tx)
        except Exception as e:
            self.ConfigObj.logger.warning(
                f"Failed to estimate gas for transaction because the transaction is likely fail.\n"
                f"Most often this is due to an arb opportunity already being closed, but it can include other bugs\n."
                f"This is expected to happen occasionally, discarding; exception: {e}"
            )
            return None

        if self.access_lists:
            try:
                access_list = self._create_access_list(tx["data"])
                tx_after = dict(tx, {"accessList": access_list})
                estimated_gas_after = self.eth.estimate_gas(transaction=tx_after)
                if estimated_gas > estimated_gas_after:
                    estimated_gas = estimated_gas_after
                    tx = tx_after
                self.ConfigObj.logger.info(f"Access list: {access_list}\n, gas before and after: {estimated_gas}, {estimated_gas_after}")
            except Exception as e:
                self.ConfigObj.logger.info(f"Applying access list to transaction failed with {e}")

        tx["gas"] = estimated_gas + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET

        signed_tx = self.eth.account.sign_transaction(tx, self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL)

        gas_cost_wei = int(current_gas_price * estimated_gas * self.ConfigObj.EXPECTED_GAS_MODIFIER)

        if self.ConfigObj.network.GAS_ORACLE_ADDRESS:
            gas_cost_wei += asyncio.get_event_loop().run_until_complete(
                asyncio.gather(
                    self.ConfigObj.GAS_ORACLE_CONTRACT.caller.getL1Fee(
                        signed_tx.rawTransaction
                    )
                )
            )

        gas_cost_eth = Decimal(gas_cost_wei) / ETH_DECIMALS
        gas_gain_eth = expected_profit_gastkn * self.ConfigObj.ARB_REWARDS_PPM / 1_000_000

        gas_cost_usd = gas_cost_eth * expected_profit_usd / expected_profit_gastkn
        gas_gain_usd = expected_profit_usd * self.ConfigObj.ARB_REWARDS_PPM / 1_000_000

        self.ConfigObj.logger.info(
            log_format(
                log_name="arb_with_gas",
                log_data={**log_object, "block_number": block_number, "tx": tx}
            )
        )

        self.ConfigObj.logger.info(
            f"[helpers.txhelpers.validate_and_submit_transaction]:\n"
            f"- Expected cost: {num_format(gas_cost_eth)} GAS token ({num_format(gas_cost_usd)} USD)\n"
            f"- Expected gain: {num_format(gas_gain_eth)} GAS token ({num_format(gas_gain_usd)} USD)\n"
        )

        if gas_gain_eth > gas_cost_eth:
            self.ConfigObj.logger.info("Attempting to execute profitable arb transaction...")
            try:
                if self.use_tenderly:
                    tx_hash = self.eth.send_raw_transaction(signed_tx.rawTransaction)
                else:
                    tx_hash = self._send_private_transaction(signed_tx, block_number)
            except Exception as e:
                self.ConfigObj.logger.info(f"Transaction execution failed with {e}")
                return None
            self._wait_for_transaction_receipt(tx_hash)
            return tx_hash
        else:
            self.ConfigObj.logger.info("Not attempting to execute non-profitable arb transaction...")
            return None

    def check_and_approve_tokens(self, tokens: List):
        """
        This function checks if tokens have been previously approved from the wallet address to the Arbitrage contract.
        If they are not already approved, it will submit approvals for each token specified in Flashloan tokens.
        :param tokens: the list of tokens to check/approve
        """

        for token_address in [token for token in tokens if token != self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS]:
            token_contract = self.eth.contract(address=token_address, abi=ERC20_ABI)
            allowance = token_contract.caller.allowance(self.wallet_address, self.arb_contract.address)
            self.ConfigObj.logger.info(f"Remaining allowance for token {token_address} = {allowance}")
            if allowance == 0:
                function = token_contract.functions.approve(self.arb_contract.address, MAX_UINT256)
                tx, _, _ = self._build_transaction(function=function, value=0)
                if tx is not None:
                    signed_tx = self.eth.account.sign_transaction(tx, self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL)
                    tx_hash = self.eth.send_raw_transaction(signed_tx.rawTransaction)
                    self._wait_for_transaction_receipt(tx_hash)

    def _build_transaction(self, function, value):
        nonce = self.eth.get_transaction_count(self.wallet_address)
        block = self.eth.get_block("pending")
        base_fee_per_gas = block["baseFeePerGas"]

        tx_details = {
            "nonce": nonce,
            "value": value,
            "from": self.wallet_address
        }

        if self.use_eip_1559:
            max_priority_fee_per_gas = int(self._max_priority_fee_per_gas() * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET)
            current_gas_price = base_fee_per_gas + max_priority_fee_per_gas
            current_gas_price_key = "maxFeePerGas"
            tx_details["type"] = 2
            tx_details["maxPriorityFeePerGas"] = max_priority_fee_per_gas
        else:
            current_gas_price = base_fee_per_gas
            current_gas_price_key = "gasPrice"
            tx_details["type"] = 1

        while True:
            tx_details[current_gas_price_key] = current_gas_price
            try:
                tx = function.build_transaction(tx_details)
                break
            except Exception as e:
                self.ConfigObj.logger.info(f"Failed building transaction {tx_details}; exception {e}")
                message_parts = str(e).split("baseFee: ")
                if len(message_parts) > 1:
                    current_gas_price = int_prefix(message_parts[1])
                else:
                    tx = None
                    break

        return tx, current_gas_price, block["number"]

    def _max_priority_fee_per_gas(self):
        response = requests.post(
            self.ConfigObj.RPC_URL,
            json={"id": 1, "jsonrpc": "2.0", "method": "eth_maxPriorityFeePerGas"},
            headers={"accept": "application/json", "content-type": "application/json"}
        )
        return int(loads(response.text)["result"].split("0x")[1], 16)

    def _create_access_list(self, data):
        response = requests.post(
            self.ConfigObj.RPC_URL,
            json = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_createAccessList",
                "params": [
                    {
                        "from": self.wallet_address,
                        "to": self.arb_contract.address,
                        "data": data
                    }
                ]
            }
        )
        return loads(response.text)["result"]["accessList"]

    def _send_private_transaction(self, signed_tx, block_number):
        response = self.alchemy.core.provider.make_request(
            method="eth_sendPrivateTransaction",
            params=[
                {
                    "tx": signed_tx.rawTransaction.hex(),
                    "maxBlockNumber": block_number + 10,
                    "preferences": {"fast": True}
                }
            ],
            method_name="eth_sendPrivateTransaction",
            headers={"accept": "application/json", "content-type": "application/json"}
        )
        return response["result"]

    def _wait_for_transaction_receipt(self, tx_hash):
        try:
            tx_receipt = self.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_hash == tx_receipt["transactionHash"]
            self.ConfigObj.logger.info(f"Transaction {tx_hash} completed")
        except TimeExhausted as _:
            self.ConfigObj.logger.info(f"Transaction {tx_hash} timeout (stuck in mempool); moving on")
