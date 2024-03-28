"""
This module is used to build the parameters for the test pool. It is used to build the parameters for the test pool and
encode them into a string that can be used to update the storage of the pool contract.

(c) Copyright Bprotocol foundation 2024.
All rights reserved.
Licensed under MIT License.
"""
import argparse
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import eth_abi
from web3 import Web3
from web3.types import RPCEndpoint

from fastlane_bot.tests.deterministic.dtest_pool import TestPool


@dataclass
class TestPoolParam:
    """
    This class is used to represent a parameter of the test pool.
    """

    type: str
    value: any


class TestPoolParamsBuilder:
    """
    This class is used to build the parameters for the test pool.
    """

    def __init__(self, args: argparse.Namespace, w3: Web3):
        self.w3 = w3
        self.args = args

    @staticmethod
    def convert_to_bool(value: str or int) -> bool:
        """
        This method is used to convert a string value to a boolean.
        """
        if isinstance(value, str):
            return value.lower() in ["true", "1"]
        return bool(value)

    def safe_int_conversion(self, value: Any) -> int or None:
        """
        This method is used to convert a value to an integer.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            self.args.logger.error(f"Error converting {value} to int")
            return None

    def append_zeros(self, value: any, type_str: str) -> str:
        """
        This method is used to append zeros to a value based on the type.
        """
        result = None
        if type_str == "bool":
            result = "0001" if str(value).lower() in {"true", "1"} else "0000"
        elif type_str == "int24":
            long_hex = eth_abi.encode(["int24"], [value]).hex()
            result = long_hex[-6:]
        elif "int" in type_str:
            try:
                hex_value = hex(value)[2:]
                length = int(re.search(r"\d+", type_str).group()) // 4
                result = "0" * (length - len(hex_value)) + hex_value
            except Exception as e:
                self.args.logger.error(f"Error building append_zeros {str(e)}")
        return result

    def build_type_val_dict(
        self, pool: TestPool, param_list_single: List[str]
    ) -> Tuple:
        """
        This method is used to build the type_val_dict and the encoded_params for the given pool.
        """
        type_val_dict = {}
        for param in param_list_single:
            param_value = self.get_param_value(pool, param)
            if param_value is not None:
                type_val_dict[param] = TestPoolParam(
                    type=pool.__getattribute__(f"param_{param}_type") or "uint256",
                    value=param_value,
                )

        encoded_params = self.encode_params(type_val_dict, param_list_single)
        return type_val_dict, encoded_params

    def get_param_value(self, pool: TestPool, param: str) -> int or bool:
        """
        This method is used to get the value of the given parameter.
        """
        if param == "blockTimestampLast":
            return self.get_latest_block_timestamp()
        elif param == "unlocked":
            return self.convert_to_bool(pool.param_unlocked)
        else:
            return self.safe_int_conversion(
                pool.__getattribute__(f"param_{param}") or 0
            )

    def get_latest_block_timestamp(self):
        """
        This method is used to get the latest block timestamp.
        """
        try:
            return int(self.w3.eth.get_block("latest")["timestamp"])
        except Exception as e:
            self.args.logger.error(f"Error fetching latest block timestamp: {e}")
            return None

    def encode_params(self, type_val_dict: Dict, param_list_single: List[str]) -> str:
        """
        This method is used to encode the parameters into a string that can be used to update the storage of the pool
        contract.

        Args:
            type_val_dict (dict): The type value dictionary.
            param_list_single (list): The list of parameters.

        Returns:
            str: The encoded parameters.
        """
        try:
            result = "".join(
                self.append_zeros(type_val_dict[param].value, type_val_dict[param].type)
                for param in param_list_single
            )
            return "0x" + "0" * (64 - len(result)) + result
        except Exception as e:
            self.args.logger.error(f"Error encoding params: {e}, {type_val_dict}")
            return None

    def get_update_params_dict(self, pool: TestPool) -> Dict:
        """
        This method is used to get the update parameters dictionary for the given pool.

        Args:
            pool (TestPool): The test pool.

        Returns:
            dict: The update parameters dictionary.
        """
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

    def set_storage_at(self, pool_address: str, update_params_dict_single: Dict):
        method = RPCEndpoint("tenderly_setStorageAt")
        self.w3.provider.make_request(
            method=method,
            params=[
                pool_address,
                update_params_dict_single["slot"],
                update_params_dict_single["encoded_params"],
            ],
        )
        self.args.logger.debug(f"[set_storage_at] {pool_address}, {update_params_dict_single['slot']}")
        self.args.logger.debug(
            f"[set_storage_at] Updated storage parameters for {pool_address} at slot {update_params_dict_single['slot']}"
        )

    @staticmethod
    def update_pools_by_exchange(args, builder, pools, w3):
        # Handle each exchange_type differently for the required updates
        for pool in pools:
            # Set balances on pool
            pool.set_balance_via_faucet(args, w3, 0)
            pool.set_balance_via_faucet(args, w3, 1)

            # Set storage parameters
            update_params_dict = builder.get_update_params_dict(pool)

            # Update storage parameters
            for slot, params in update_params_dict.items():
                builder.set_storage_at(pool.pool_address, params)
                args.logger.debug(
                    f"Updated storage parameters for {pool.pool_address} at slot {slot}"
                )
