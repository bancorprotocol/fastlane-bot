import argparse
import ast
import glob
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime

import eth_abi
import pandas as pd
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.contract import Contract
from web3.types import RPCEndpoint

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI, ERC20_ABI
from fastlane_bot.tests.deterministic.constants import (
    DEFAULT_GAS,
    DEFAULT_GAS_PRICE,
    ETH_ADDRESS,
    BNT_ADDRESS,
    TEST_MODE_AMT,
    USDC_ADDRESS,
    USDT_ADDRESS,
    SUPPORTED_EXCHANGES,
)
from fastlane_bot.tools.cpc import T


class Web3Manager:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.w3.is_connected(), "Web3 not connected"

    def get_carbon_controller(self, address: Address):
        return self.w3.eth.contract(address=address, abi=CARBON_CONTROLLER_ABI)

    @staticmethod
    def get_carbon_controller_address(multichain_addresses_path: str, network: str):
        # Initialize the Carbon Controller contract
        lookup_table = pd.read_csv(multichain_addresses_path)
        return (
            lookup_table.query("exchange_name=='carbon_v1'")
            .query(f"chain=='{network}'")
            .factory_address.values[0]
        )


@dataclass
class Token:
    address: str or Address  # Address after __post_init__, str before

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)
        self._contract = None

    @property
    def contract(self):
        return self._contract

    @contract.setter
    def contract(self, contract: Contract):
        self._contract = contract

    @property
    def is_eth(self):
        return self.address == ETH_ADDRESS


@dataclass
class TokenBalance:
    token: Token or str  # Token after __post_init__, str before
    balance: int

    def __post_init__(self):
        self.token = Token(self.token)
        self.balance = int(self.balance)

    @property
    def hex_balance(self):
        return Web3.to_hex(self.balance)

    def faucet_params(self, wallet_address: str = None) -> list:
        return (
            [[self.token.address], self.hex_balance]
            if self.token.is_eth
            else [self.token.address, wallet_address, self.hex_balance]
        )


@dataclass
class Wallet:
    w3: Web3
    address: str or Address  # Address after __post_init__, str before
    balances: list[
        TokenBalance or dict
    ] = None  # List of TokenBalances after __post_init__, list of dicts before

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)
        self.balances = [TokenBalance(**args) for args in self.balances or []]

    @property
    def nonce(self):
        return self.w3.eth.get_transaction_count(self.address)


@dataclass
class Strategy:
    w3: Web3
    token0: Token
    token1: Token
    y0: int
    z0: int
    A0: int
    B0: int
    y1: int
    z1: int
    A1: int
    B1: int
    wallet: Wallet

    @property
    def id(self):
        return self._id or None

    @id.setter
    def id(self, id: int):
        self._id = id

    def __post_init__(self):
        self.token0 = Token(self.token0)
        self.token0.contract = self.w3.eth.contract(
            address=self.token0.address, abi=ERC20_ABI
        )
        self.token1 = Token(self.token1)
        self.token1.contract = self.w3.eth.contract(
            address=self.token1.address, abi=ERC20_ABI
        )
        self.wallet = Wallet(self.w3, self.wallet)

    def get_token_approval(
        self, token_id: int, approval_address: ChecksumAddress
    ) -> str:
        token = self.token0 if token_id == 0 else self.token1
        if token.address in [
            BNT_ADDRESS,
            USDC_ADDRESS,
            USDT_ADDRESS,
        ]:  # TODO: Ask Nick about this?
            function_call = token.contract.functions.approve(
                approval_address, 0
            ).transact(
                {
                    "gasPrice": DEFAULT_GAS_PRICE,
                    "gas": DEFAULT_GAS,
                    "from": self.wallet.address,
                    "nonce": self.wallet.nonce,
                }
            )
            tx_reciept = self.w3.eth.wait_for_transaction_receipt(function_call)
            tx_hash = self.w3.to_hex(dict(tx_reciept)["transactionHash"])

            if dict(tx_reciept)["status"] != 1:
                print("Approval Failed")
            else:
                print("Successfully Approved for 0")

            print(f"tx_hash = {tx_hash}")

        function_call = token.contract.functions.approve(
            approval_address, TEST_MODE_AMT
        ).transact(
            {
                "gasPrice": DEFAULT_GAS_PRICE,
                "gas": DEFAULT_GAS,
                "from": self.wallet.address,
                "nonce": self.wallet.nonce,
            }
        )
        tx_reciept = self.w3.eth.wait_for_transaction_receipt(function_call)
        tx_hash = self.w3.to_hex(dict(tx_reciept)["transactionHash"])

        if dict(tx_reciept)["status"] != 1:
            print("Approval Failed")
        else:
            print("Successfully Approved Token for Unlimited")

        print(f"tx_hash = {tx_hash}")
        return tx_hash

    @property
    def value(self):
        return (
            self.y0 if self.token0.is_eth else self.y1 if self.token1.is_eth else None
        )


@dataclass
class TestPool:
    exchange_type: str
    pool_address: str
    tkn0_address: str
    tkn1_address: str
    slots: str or list  # List after __post_init__, str before
    param_lists: str or list  # List after __post_init__, str before
    tkn0_setBalance: TokenBalance or int  # TokenBalance after __post_init__, int before
    tkn1_setBalance: TokenBalance or int  # TokenBalance after __post_init__, int before
    param_blockTimestampLast: int = None
    param_blockTimestampLast_type: str = None
    param_reserve0: int = None
    param_reserve0_type: str = None
    param_reserve1: int = None
    param_reserve1_type: str = None
    param_liquidity: int = None
    param_liquidity_type: str = None
    param_sqrtPriceX96: int = None
    param_sqrtPriceX96_type: str = None
    param_tick: int = None
    param_tick_type: str = None
    param_observationIndex: int = None
    param_observationIndex_type: str = None
    param_observationCardinality: int = None
    param_observationCardinality_type: str = None
    param_observationCardinalityNext: int = None
    param_observationCardinalityNext_type: str = None
    param_feeProtocol: int = None
    param_feeProtocol_type: str = None
    param_unlocked: int = None
    param_unlocked_type: str = None

    def __post_init__(self):
        self.slots = ast.literal_eval(self.slots)
        self.param_lists = ast.literal_eval(self.param_lists)

    @staticmethod
    def attributes():
        return list(TestPool.__dataclass_fields__.keys())

    @property
    def param_dict(self):
        return dict(zip(self.slots, self.param_lists))

    @property
    def is_supported(self):
        return self.exchange_type in SUPPORTED_EXCHANGES

    def set_balance_via_faucet(self, w3: Web3, token_id: int):
        token_address = self.tkn0_address if token_id == 0 else self.tkn1_address
        amount_wei = self.tkn0_setBalance if token_id == 0 else self.tkn1_setBalance
        token_balance = TokenBalance(token=token_address, balance=amount_wei)
        params = token_balance.faucet_params(wallet_address=self.pool_address)
        method_name = RPCEndpoint(
            "tenderly_setBalance"
            if token_balance.token.is_eth
            else "tenderly_setErc20Balance"
        )
        w3.provider.make_request(method=method_name, params=params)
        token_balance.balance = amount_wei
        if token_id == 0:
            self.tkn0_setBalance = token_balance
        else:
            self.tkn1_setBalance = token_balance
        print(f"Reset Balance to {amount_wei}")


@dataclass
class Param:
    type: str
    value: any


class PoolParamsBuilder:
    def __init__(self, w3: Web3):
        self.w3 = w3

    @staticmethod
    def convert_to_bool(value: str or int) -> bool:
        if isinstance(value, str):
            return value.lower() in ["true", "1"]
        return bool(value)

    @staticmethod
    def safe_int_conversion(value: any) -> int or None:
        try:
            return int(value)
        except (ValueError, TypeError):
            print(f"Error converting {value} to int")
            return None

    @staticmethod
    def append_zeros(value: any, type_str: str) -> str:
        result = None
        if type_str == "bool":
            result = "0001" if value.lower() in ["true", "1"] else "0000"
        elif type_str == "int24":
            long_hex = eth_abi.encode(["int24"], [value]).hex()
            result = long_hex[-6:]
        elif "int" in type_str:
            try:
                hex_value = hex(value)[2:]
                length = int(re.search(r"\d+", type_str).group()) // 4
                result = "0" * (length - len(hex_value)) + hex_value
            except Exception as e:
                print(f"Error building append_zeros {str(e)}")
        return result

    def build_type_val_dict(self, pool: TestPool, param_list_single: list[str]):
        type_val_dict = {}
        for param in param_list_single:
            param_value = self.get_param_value(pool, param)
            if param_value is not None:
                type_val_dict[param] = Param(
                    type=pool.__getattribute__(f"param_{param}_type") or "uint256",
                    value=param_value,
                )

        encoded_params = self.encode_params(type_val_dict, param_list_single)
        return type_val_dict, encoded_params

    def get_param_value(self, pool: TestPool, param: str) -> int or bool:
        if param == "blockTimestampLast":
            return self.get_latest_block_timestamp()
        elif param == "unlocked":
            return self.convert_to_bool(pool.param_unlocked)
        else:
            return self.safe_int_conversion(
                pool.__getattribute__(f"param_{param}") or 0
            )

    def get_latest_block_timestamp(self):
        try:
            return int(self.w3.eth.get_block("latest")["timestamp"])
        except Exception as e:
            print(f"Error fetching latest block timestamp: {e}")
            return None

    def encode_params(self, type_val_dict: dict, param_list_single: list[str]) -> str:
        try:
            result = "".join(
                self.append_zeros(type_val_dict[param].value, type_val_dict[param].type)
                for param in param_list_single
            )
            return "0x" + "0" * (64 - len(result)) + result
        except Exception as e:
            print(f"Error encoding params: {e}, {type_val_dict}")
            return None

    def get_update_params_dict(self, pool: TestPool):
        params_dict = {}
        for i in range(len(pool.slots)):
            params_dict[pool.slots[i]] = {
                "slot": "0x" + self.append_zeros(int(pool.slots[i]), "uint256")
            }
            type_val_dict, encoded_params = self.build_type_val_dict(
                pool, param_list_single=pool.param_lists[i]
            )

            params_dict[pool.slots[i]]["type_val_dict"] = type_val_dict
            params_dict[pool.slots[i]]["encoded_params"] = encoded_params
        return params_dict

    def set_storage_at(self, pool_address: str, update_params_dict_single: dict):
        method = RPCEndpoint("tenderly_setStorageAt")
        self.w3.provider.make_request(
            method=method,
            params=[
                pool_address,
                update_params_dict_single["slot"],
                update_params_dict_single["encoded_params"],
            ],
        )
        print(f"[set_storage_at] {pool_address}, {update_params_dict_single['slot']}")
        print(
            f"[set_storage_at] Updated storage parameters for {pool_address} at slot {update_params_dict_single['slot']}"
        )


class StrategyManager:
    """
    A class to manage Carbon strategies.

    Attributes:
        w3 (Web3): The Web3 instance.
        carbon_controller (Contract): The CarbonController contract instance.
    """

    def __init__(self, w3: Web3, carbon_controller: Contract):
        self.w3 = w3
        self.carbon_controller = carbon_controller

    @staticmethod
    def process_order_data(log_args: dict, order_key: str) -> dict:
        """Transforms nested order data by appending a suffix to each key.

        Args:
            log_args (dict): The log arguments.
            order_key (str): The key to process.

        Returns:
            dict: The processed order data.
        """
        if order_data := log_args.get(order_key):
            suffix = order_key[-1]  # Assumes order_key is either 'order0' or 'order1'
            return {f"{key}{suffix}": value for key, value in order_data.items()}
        return {}

    @staticmethod
    def print_state_changes(
        all_carbon_strategies: list,
        deleted_strategies: list,
        remaining_carbon_strategies: list,
    ) -> None:
        """
        Prints the state changes of Carbon strategies.

        Args:
            all_carbon_strategies (list): The list of all Carbon strategies.
            deleted_strategies (list): The list of deleted Carbon strategies.
            remaining_carbon_strategies (list): The list of remaining Carbon strategies.
        """
        print(f"{len(all_carbon_strategies)} Carbon strategies have been created")
        print(f"{len(deleted_strategies)} Carbon strategies have been deleted")
        print(f"{len(remaining_carbon_strategies)} Carbon strategies remain")

    def get_generic_events(self, event_name: str, from_block: int) -> pd.DataFrame:
        """
        Fetches logs for a specified event from a smart contract.

        Args:
            event_name (str): The name of the event.
            from_block (int): The block number to start fetching logs from.

        Returns:
            pandas.DataFrame: A DataFrame containing the logs of the specified event.
        """
        log_list = getattr(self.carbon_controller.events, event_name).get_logs(
            fromBlock=from_block
        )
        data = []
        for log in log_list:
            log_data = {
                "block_number": log["blockNumber"],
                "transaction_hash": self.w3.to_hex(log["transactionHash"]),
                **log["args"],
            }

            # Process and update log_data for 'order0' and 'order1', if present
            for order_key in ["order0", "order1"]:
                if order_data := self.process_order_data(log["args"], order_key):
                    log_data.update(order_data)
                    del log_data[order_key]

            data.append(log_data)

        df = pd.DataFrame(data)
        return (
            df.sort_values(by="block_number") if "block_number" in df.columns else df
        ).reset_index(drop=True)

    def get_state_of_carbon_strategies(self, from_block: int) -> tuple:
        """
        Fetches the state of Carbon strategies.

        Args:
            from_block (int): The block number to start fetching logs from.

        Returns: tuple: A tuple containing the DataFrames of the 'StrategyCreated' and 'StrategyDeleted' events,
        and the list of remaining Carbon strategies.
        """
        strategy_created_df = self.get_generic_events(
            event_name="StrategyCreated", from_block=from_block
        )
        all_carbon_strategies = (
            []
            if strategy_created_df.empty
            else [
                (strategy_created_df["id"][i], strategy_created_df["owner"][i])
                for i in strategy_created_df.index
            ]
        )
        strategy_deleted_df = self.get_generic_events(
            event_name="StrategyDeleted", from_block=from_block
        )
        deleted_strategies = (
            [] if strategy_deleted_df.empty else strategy_deleted_df["id"].to_list()
        )
        remaining_carbon_strategies = [
            x for x in all_carbon_strategies if x[0] not in deleted_strategies
        ]

        # Print state changes
        self.print_state_changes(
            all_carbon_strategies, deleted_strategies, remaining_carbon_strategies
        )

        # Return state changes
        return strategy_created_df, strategy_deleted_df, remaining_carbon_strategies

    def modify_tokens_for_deletion(self) -> None:
        """
        Modifies tokens for deletion.
        """
        pass

    def create_strategy(self, strategy: Strategy) -> str:
        print("Creating Strategy...")
        tx_params = {
            "from": strategy.wallet.address,
            "nonce": strategy.wallet.nonce,
            "gasPrice": DEFAULT_GAS_PRICE,
            "gas": DEFAULT_GAS,
        }
        if strategy.value:
            tx_params["value"] = strategy.value

        tx_hash = self.carbon_controller.functions.createStrategy(
            strategy.token0,
            strategy.token1,
            (
                [strategy.y0, strategy.z0, strategy.A0, strategy.B0],
                [strategy.y1, strategy.z1, strategy.A1, strategy.B1],
            ),
        ).transact(tx_params)

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status != 1:
            print("Creation Failed")
            return None
        else:
            print("Successfully Created Strategy")
            return self.w3.to_hex(tx_receipt.transactionHash)

    def delete_strategy(self, strategy_id: int, wallet: Address) -> int:
        print("Deleting Strategy...")
        nonce = self.w3.eth.get_transaction_count(wallet)
        tx_params = {
            "from": wallet,
            "nonce": nonce,
            "gasPrice": DEFAULT_GAS_PRICE,
            "gas": DEFAULT_GAS,
        }
        tx_hash = self.carbon_controller.functions.deleteStrategy(strategy_id).transact(
            tx_params
        )

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt.status

    def delete_all_carbon_strategies(self, carbon_strategy_id_owner_list: list) -> list:
        print("Deleting strategies...")
        self.modify_tokens_for_deletion()
        undeleted_strategies = []
        for strategy_id, owner in carbon_strategy_id_owner_list:
            print("Attempt 1")
            status = self.delete_strategy(strategy_id, owner)
            if status == 0:
                try:
                    strategy_info = self.carbon_controller.functions.strategy(strategy_id).call()
                    current_owner = strategy_info[1]
                    try:
                        print("Attempt 2")
                        status = self.delete_strategy(strategy_id, current_owner)
                        if status == 0:
                            print(f"Unable to delete strategy {strategy_id}")
                            undeleted_strategies += [strategy_id]
                    except Exception as e:
                        print(f"Strategy {strategy_id} not found - already deleted {e}")
                except Exception as e:
                    print(f"Strategy {strategy_id} not found - already deleted {e}")
            elif status == 1:
                print(f"Strategy {strategy_id} successfully deleted")
            else:
                print("Possible error")
        return undeleted_strategies


def scan_logs_for_success():
    time.sleep(5)

    # Set the path to the logs directory relative to your notebook's location
    path_to_logs = "./logs/*"

    # Use glob to list all directories
    log_directories = [f for f in glob.glob(path_to_logs) if os.path.isdir(f)]

    most_recent_log_folder = log_directories[-1]
    print(f"Accessing log folder {most_recent_log_folder}")
    print("Looking for pool data file...")
    most_recent_pool_data = os.path.join(
        most_recent_log_folder, "latest_pool_data.json"
    )

    while True:
        if os.path.exists(most_recent_pool_data):
            print("File found.")
            break
        else:
            print("File not found, waiting 10 seconds.")
            time.sleep(10)

    with open(most_recent_pool_data) as f:
        pool_data = json.load(f)
        print("len(pool_data)", len(pool_data))

    all_successful_txs = glob.glob(os.path.join(most_recent_log_folder, "*.txt"))

    # Read the successful_txs in as strings
    txt_all_successful_txs = []
    for successful_tx in all_successful_txs:
        with open(successful_tx, "r") as file:
            j = file.read()
            txt_all_successful_txs += [(j)]
            file.close()

    # Successful transactions on Tenderly are marked by status=1
    return [tx for tx in txt_all_successful_txs if "'status': 1" in tx]


def clean_tx_data(tx_data: dict) -> dict:
    for trade in tx_data["trades"]:
        if trade["exchange"] == "carbon_v1" and "cid0" in trade:
            del trade["cid0"]
    return tx_data


def get_tx_data(strategy_id: int, txt_all_successful_txs: list) -> dict:
    """this only handles one tx found"""
    for tx in txt_all_successful_txs:
        if str(strategy_id) in tx:
            return json.loads(tx.split("\n\n")[-1])


@dataclass
class ArgumentParserMock:
    cache_latest_only: str = "True"
    backdate_pools: str = "False"
    static_pool_data_filename: str = "static_pool_data"
    arb_mode: str = "multi_pairwise_all"
    flashloan_tokens: str = f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI},{T.USDC},{T.USDT},{T.WETH}"
    n_jobs: int = -1
    exchanges: str = "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3"
    polling_interval: int = 1
    alchemy_max_block_fetch: int = 2000
    reorg_delay: int = 0
    logging_path: str = ""
    loglevel: str = "INFO"
    use_cached_events: str = "False"
    run_data_validator: str = "False"
    randomizer: int = 3
    limit_bancor3_flashloan_tokens: str = "True"
    default_min_profit_gas_token: str = "0.01"
    timeout: int = None
    target_tokens: str = None
    replay_from_block: int = None
    tenderly_fork_id: int = None
    tenderly_event_exchanges: str = "pancakeswap_v2,pancakeswap_v3"
    increment_time: int = 1
    increment_blocks: int = 1
    blockchain: str = "ethereum"
    pool_data_update_frequency: int = -1
    use_specific_exchange_for_target_tokens: str = None
    prefix_path: str = ""
    version_check_frequency: int = 1
    self_fund: str = "False"
    read_only: str = "True"
    is_args_test: str = "False"
    rpc_url: str = None


def get_default_main_args():
    return ArgumentParserMock()


def get_test_strategies():
    test_strategies_path = os.path.normpath(
        "fastlane_bot/tests/deterministic/_data/test_strategies.json"
    )
    with open(test_strategies_path) as file:
        test_strategies = json.load(file)["test_strategies"]
        print(f"{len(test_strategies.keys())} test strategies imported")
    return test_strategies
