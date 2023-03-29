"""
This module contains the FastLaneArbBotUI class, which is the main user interface for the FastLaneArbBot.
It is responsible for collecting data from the Ethereum blockchain, and then finding arbitrage opportunities
between the supported exchanges.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from _decimal import Decimal
from dataclasses import dataclass
from typing import Any

from fastlane_bot.helpers import (
    TransactionHelpers,
    CacheHelpers,
    ValidationHelpers,
    SearchHelpers,
    TestingHelpers,
)
from fastlane_bot.networks import *

logger = ec.DEFAULT_LOGGER


@dataclass
class FastLaneArbBotUI(
    TransactionHelpers,
    CacheHelpers,
    ValidationHelpers,
    SearchHelpers,
    TestingHelpers,
):
    """
    This class is the main user interface for the FastLaneArbBot.
    It is responsible for administering the bot,
    and collecting data from the Ethereum blockchain,
    and then finding arbitrage opportunities between the supported exchanges.
    """

    # # Public attributes
    base_path: str = ec.BASE_PATH
    raiseonerror: bool = ec.DEFAULT_RAISEONERROR
    filetype: str = ec.DEFAULT_FILETYPE
    verbose: str = ec.VERBOSE
    n_jobs: int = ec.DEFAULT_N_JOBS
    backend: str = ec.DEFAULT_BACKEND
    execute_mode: str = ec.DEFAULT_EXECUTE_MODE
    search_delay: int = ec.DEFAULT_SEARCH_DELAY
    network_name: str = ec.PRODUCTION_NETWORK
    fastlane_contract_address: str = ec.FASTLANE_CONTRACT_ADDRESS
    blocktime_deviation: int = ec.DEFAULT_BLOCKTIME_DEVIATION
    max_slippage: Decimal = ec.DEFAULT_MAX_SLIPPAGE
    min_profit: Decimal = ec.DEFAULT_MIN_PROFIT
    tenderly_fork_id: str = ec.TENDERLY_FORK
    web3: Any = None
    bancor_network_info: Any = None
    _ETH_PRIVATE_KEY: str = None

    def execute(self):
        """
        Executes the arbitrage trades
        """
        df = self.cached_trade_routes
        if df is None:
            logger.info("No cached trade routes found!")
            return None

        valid_routes = self.get_and_validate_trade_routes(df)
        self.archive_trade_routes()
        logger.debug(f"Valid routes: {valid_routes}")

        if not valid_routes:
            logger.info("No valid cached trade routes!")
            return

        # Current gas price estimate
        current_gas_price = int(
            self.get_eth_gas_price_alchemy() * ec.DEFAULT_GAS_PRICE_OFFSET
        )
        current_max_priority_gas = self.get_max_priority_fee_per_gas_alchemy()

        # Use current Bancor V3 BNT/ETH liquidity to convert gas price to BNT
        bnt, eth = self.get_bnt_eth_liquidity()

        block_number = self.web3.eth.get_block("latest")["number"]

        try:
            for src_amt, trade_path, bnt_profit in valid_routes:
                # Get the trade path
                if trade_path:
                    logger.info("Found a trade. Executing...")
                    logger.info(
                        f"\nRoute to execute: routes: {trade_path}, sourceAmount: {src_amt}, expected_profit {bnt_profit} \n\n"
                    )
                    logger.info(f"current gas price = {current_gas_price}")
                    nonce = self.get_nonce()
                    if self.network_name in ec.VALID_TENDERLY_NETWORKS:
                        tx_receipt = self.build_transaction_tenderly(
                            routes=trade_path,
                            src_amt=src_amt,
                            nonce=nonce,
                        )

                    # get estimate of gas used for transaction
                    if self.network_name == ec.PRODUCTION_NETWORK_NAME:
                        # Build the transaction
                        arb_tx = self.build_transaction_with_gas(
                            routes=trade_path,
                            src_amt=src_amt,
                            gas_price=current_gas_price,
                            max_priority=current_max_priority_gas,
                            nonce=nonce,
                        )
                        if arb_tx is None:
                            break
                        gas_estimate = arb_tx["gas"]

                        current_gas_price = (
                            arb_tx["maxFeePerGas"] + arb_tx["maxPriorityFeePerGas"]
                        )
                        gas_estimate = int(gas_estimate + ec.DEFAULT_GAS_SAFETY_OFFSET)
                        logger.info(f"gas estimate = {gas_estimate}")
                        current_gas_price = int(
                            current_gas_price * ec.DEFAULT_GAS_PRICE_OFFSET
                        )
                        # calculate the cost of gas in BNT
                        gas_in_bnt = self.estimate_gas_in_bnt(
                            gas_price=current_gas_price,
                            gas_estimate=gas_estimate,
                            bnt=bnt,
                            eth=eth,
                        )
                        logger.info(f"estimate gas cost in BNT: {gas_in_bnt}")
                        # calculate the break-even gas price that we can pay
                        break_even_gas_price = self.get_break_even_gas_price(
                            gas_estimate=gas_estimate,
                            bnt_profit=bnt_profit,
                            bnt=bnt,
                            eth=eth,
                        )
                        logger.info(
                            f"current gas price = {current_gas_price}, breakeven gas price = {break_even_gas_price}, diff = {current_gas_price - break_even_gas_price}"
                        )

                        adjusted_reward = Decimal(
                            Decimal(bnt_profit) * ec.DEFAULT_REWARD_PERCENT
                        )

                        if adjusted_reward > gas_in_bnt:
                            logger.info(
                                f"Expected profit of {bnt_profit} BNT vs cost of {gas_in_bnt} BNT in gas, executing"
                            )

                            # Submit the transaction
                            tx_receipt = self.submit_private_transaction(
                                arb_tx=arb_tx, block_number=block_number
                            )

                            if tx_receipt is None:
                                break
                        else:
                            logger.info(
                                f"Gas price too expensive! profit of {adjusted_reward} BNT vs gas cost of {gas_in_bnt} BNT. Abort, abort!"
                            )
                            break

                    # Get the transaction hash
                    tx_hash = self.web3.toHex(dict(tx_receipt)["transactionHash"])
                    # Log the transaction hash and receipt for debugging
                    logger.debug(f"Trade executed: hash = {tx_hash}, {tx_receipt}")

                    # Check if the transaction was successful
                    success = dict(tx_receipt)["status"] == 1

                    # Log the transaction success
                    logger.info(
                        f"Execute arb successful! " f"tx_hash = {tx_hash}"
                    ) if success else logger.error(
                        f"Execute transaction failed, route={trade_path}\ntx_hash = {tx_hash}"
                    )

                    # Get the block number of the transaction
                    block_number = int(dict(tx_receipt)["blockNumber"])

                    # Export the trade to a pandas dataframe and log it in the /transactions folder (or ec.TX_PATH)
                    self.trade_to_pandas(
                        tx_hash=tx_hash,
                        transaction_success=success,
                        block_number=block_number,
                        flash_loan_amt=src_amt,
                        routes=trade_path,
                        profit=bnt_profit,
                    )

                    if success:
                        break
                    break
                else:
                    logger.info("No trades executed!")

        except Exception as e:
            logger.error(f"Failed to submit trade due to exception: {e}")

    def __post_init__(self):
        # Configure the web3 instance
        web3 = (
            Web3(Web3.HTTPProvider(ec.TENDERLY_FORK_RPC))
            if self.network_name in ec.VALID_TENDERLY_NETWORKS
            else Web3(Web3.HTTPProvider(ec.ETHEREUM_MAINNET_PROVIDER))
        )
        self.web3: Web3 = web3

        # Set the local account
        self.local_account = web3.eth.account.from_key(self._ETH_PRIVATE_KEY)

        # Set the public address
        self.wallet_address = str(self.local_account.address)

        # Set the arb contract
        self.arb_contract = web3.eth.contract(
            address=web3.toChecksumAddress(self.fastlane_contract_address),
            abi=ec.FAST_LANE_CONTRACT_ABI,
        )
