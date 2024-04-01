"""
Transaction handlers for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__ = "01/May/2023"

from _decimal import Decimal

from dataclasses import dataclass
from typing import List, Any, Dict

from alchemy import Network, Alchemy
from web3.exceptions import TimeExhausted

from fastlane_bot.config import Config
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.utils import num_format, log_format

MAX_UINT256 = 2 ** 256 - 1
ETH_RESOLUTION = 10 ** 18

@dataclass
class TxHelpers:
    """
    This class is used to organize web3 transaction tools.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    cfg: Config

    def __post_init__(self):
        self.arb_contract = self.cfg.BANCOR_ARBITRAGE_CONTRACT
        self.use_tenderly = self.cfg.NETWORK == self.cfg.NETWORK_TENDERLY
        self.use_eip_1559 = self.cfg.NETWORK in [self.cfg.NETWORK_ETHEREUM, self.cfg.NETWORK_BASE]
        self.use_access_lists = self.cfg.NETWORK in [self.cfg.NETWORK_ETHEREUM]
        self.arb_rewards_portion = Decimal(self.cfg.ARB_REWARDS_PPM) / 1_000_000

        if self.use_tenderly:
            self.wallet_address = self.cfg.BINANCE14_WALLET_ADDRESS
        else:
            self.wallet_address = str(self.cfg.w3.eth.account.from_key(self.cfg.ETH_PRIVATE_KEY_BE_CAREFUL).address)
            self.alchemy = Alchemy(api_key=self.cfg.WEB3_ALCHEMY_PROJECT_ID, network=Network.ETH_MAINNET, max_retries=3)

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

        self.cfg.logger.info("[helpers.txhelpers.validate_and_submit_transaction] Validating trade...")
        self.cfg.logger.debug(
            f"[helpers.txhelpers.validate_and_submit_transaction]:\n"
            f"- Routes: {route_struct}\n"
            f"- Source amount: {src_amt}\n"
            f"- Source token: {src_address}\n"
            f"- Expected profit: {num_format(expected_profit_gastkn)} GAS token ({num_format(expected_profit_usd)} USD)\n"
        )

        if self.cfg.SELF_FUND:
            function = self.arb_contract.functions.fundAndArb(route_struct, src_address, src_amt)
            value = src_amt if src_address == self.cfg.NATIVE_GAS_TOKEN_ADDRESS else 0
        else:
            function = self.arb_contract.functions.flashloanAndArbV2(flashloan_struct, route_struct)
            value = 0

        tx, gas_price = self._build_transaction(function=function, value=value)
        if tx is None:
            return None

        if self.use_access_lists:
            try:
                result = self.cfg.w3.eth.create_access_list(tx)
                if tx["gas"] > result["gasUsed"]:
                    tx["gas"] = result["gasUsed"]
                    tx["accessList"] = [{"address": item["address"], "storageKeys": [key.hex() for key in item["storageKeys"]]} for item in result["accessList"]]
            except Exception as e:
                self.cfg.logger.info(f"create_access_list({tx}) failed with {e}")

        tx["gas"] += self.cfg.DEFAULT_GAS_SAFETY_OFFSET

        raw_tx = self.cfg.w3.eth.account.sign_transaction(tx, self.cfg.ETH_PRIVATE_KEY_BE_CAREFUL).rawTransaction

        gas_cost_wei = int(tx["gas"] * gas_price * self.cfg.EXPECTED_GAS_MODIFIER)
        if self.cfg.network.GAS_ORACLE_ADDRESS:
            gas_cost_wei += self.cfg.GAS_ORACLE_CONTRACT.caller.getL1Fee(raw_tx)

        gas_cost_eth = Decimal(gas_cost_wei) / ETH_RESOLUTION
        gas_cost_usd = gas_cost_eth * expected_profit_usd / expected_profit_gastkn

        gas_gain_eth = self.arb_rewards_portion * expected_profit_gastkn
        gas_gain_usd = self.arb_rewards_portion * expected_profit_usd

        self.cfg.logger.info(log_format(log_name="arb_with_gas", log_data={**log_object, "tx": tx}))

        self.cfg.logger.info(
            f"[helpers.txhelpers.validate_and_submit_transaction]:\n"
            f"- Expected cost: {num_format(gas_cost_eth)} GAS token ({num_format(gas_cost_usd)} USD)\n"
            f"- Expected gain: {num_format(gas_gain_eth)} GAS token ({num_format(gas_gain_usd)} USD)\n"
        )

        if gas_gain_eth > gas_cost_eth:
            self.cfg.logger.info("Attempting to execute profitable arb transaction")
            try:
                if self.use_tenderly:
                    tx_hash = self.cfg.w3.eth.send_raw_transaction(raw_tx)
                else:
                    tx_hash = self._send_private_transaction(raw_tx)
            except Exception as e:
                self.cfg.logger.info(f"Transaction execution failed with {e}")
                return None
            self._wait_for_transaction_receipt(tx_hash)
            return tx_hash
        else:
            self.cfg.logger.info("Discarding non-profitable arb transaction")
            return None

    def check_and_approve_tokens(self, tokens: List):
        """
        This function checks if tokens have been previously approved from the wallet address to the Arbitrage contract.
        If they are not already approved, it will submit approvals for each token specified in Flashloan tokens.
        :param tokens: the list of tokens to check/approve
        """

        for token_address in [token for token in tokens if token != self.cfg.NATIVE_GAS_TOKEN_ADDRESS]:
            token_contract = self.cfg.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            allowance = token_contract.caller.allowance(self.wallet_address, self.arb_contract.address)
            self.cfg.logger.info(f"Remaining allowance for token {token_address} = {allowance}")
            if allowance == 0:
                function = token_contract.functions.approve(self.arb_contract.address, MAX_UINT256)
                tx, _ = self._build_transaction(function=function, value=0)
                if tx is not None:
                    raw_tx = self.cfg.w3.eth.account.sign_transaction(tx, self.cfg.ETH_PRIVATE_KEY_BE_CAREFUL).rawTransaction
                    tx_hash = self.cfg.w3.eth.send_raw_transaction(raw_tx)
                    self._wait_for_transaction_receipt(tx_hash)

    def _build_transaction(self, function, value):
        tx_details = {
            "from": self.wallet_address,
            "value": value,
            "nonce": self.cfg.w3.eth.get_transaction_count(self.wallet_address)
        }

        gas_price = int(self.cfg.w3.eth.gas_price * self.cfg.DEFAULT_GAS_PRICE_OFFSET)

        if self.use_eip_1559:
            max_priority_fee = int(self.cfg.w3.eth.max_priority_fee * self.cfg.DEFAULT_GAS_PRICE_OFFSET)
            gas_price += max_priority_fee
            tx_details["type"] = 2
            tx_details["maxPriorityFeePerGas"] = max_priority_fee
            tx_details["maxFeePerGas"] = gas_price
        else:
            tx_details["type"] = 1
            tx_details["gasPrice"] = gas_price

        try:
            tx = function.build_transaction(tx_details)
            return tx, gas_price
        except Exception as e:
            self.cfg.logger.info(f"Failed building transaction {tx_details}; exception {e}")
            return None, None

    def _send_private_transaction(self, raw_tx):
        response = self.alchemy.core.provider.make_request(
            method="eth_sendPrivateTransaction",
            params=[{"tx": raw_tx, "maxBlockNumber": self.cfg.w3.eth.block_number + 10, "preferences": {"fast": True}}],
            method_name="eth_sendPrivateTransaction",
            headers={"accept": "application/json", "content-type": "application/json"}
        )
        return response["result"]

    def _wait_for_transaction_receipt(self, tx_hash):
        try:
            tx_receipt = self.cfg.w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_hash == tx_receipt["transactionHash"]
            self.cfg.logger.info(f"Transaction {tx_hash} completed")
        except TimeExhausted as _:
            self.cfg.logger.info(f"Transaction {tx_hash} timeout (stuck in mempool); moving on")
