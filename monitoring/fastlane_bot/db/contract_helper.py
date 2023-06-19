"""
Helpers for the DB components of the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

import brownie
import requests
from brownie import Contract
from brownie.network.web3 import Web3

# import fastlane_bot.config as c
import fastlane_bot.data.abi as _abi
from fastlane_bot.config import Config
from fastlane_bot.data import abi


@dataclass
class ContractHelper:
    """
    Helper for contract-related functions in the DB components of the Fastlane project.

    Parameters
    ----------
    ConfigObj: Config
        Config object
    contracts: Dict[str, Contract]
        Dictionary of contract names and their corresponding Contract objects
    filters: List[Any]
        List of event filters

    """

    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"
    ConfigObj: Config
    contracts: Dict[str, Any] = field(default_factory=dict, init=False)
    filters: List[Any] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.c = self.ConfigObj
        if self.ConfigObj.CARBON_V1_NAME not in self.contracts:
            self.contracts[self.ConfigObj.CARBON_V1_NAME] = {}
        if "CARBON_CONTROLLER_CONTRACT" not in self.contracts[self.ConfigObj.CARBON_V1_NAME]:
            self.contracts[self.ConfigObj.CARBON_V1_NAME][
                "CARBON_CONTROLLER_CONTRACT"] = self.initialize_contract_with_abi(
                self.ConfigObj.CARBON_CONTROLLER_ADDRESS, abi.CARBON_CONTROLLER_ABI
            )
        self.filters = self.get_event_filters(self.c.S)
        self.poll_interval: int = self.ConfigObj.DEFAULT_POLL_INTERVAL
        self.contracts = {}
        self.filters = []

    @property
    def carbon_controller(self) -> Contract:
        """
        Returns the CarbonController contract
        """
        if self.ConfigObj.CARBON_V1_NAME not in self.contracts:
            self.contracts[self.ConfigObj.CARBON_V1_NAME] = {}
        if "CARBON_CONTROLLER_CONTRACT" not in self.contracts[self.ConfigObj.CARBON_V1_NAME]:
            self.contracts[self.ConfigObj.CARBON_V1_NAME][
                "CARBON_CONTROLLER_CONTRACT"] = self.c.w3.eth.contract(
                address=self.ConfigObj.CARBON_CONTROLLER_ADDRESS,
                abi=abi.CARBON_CONTROLLER_ABI,
            ).functions
        return self.contracts[self.ConfigObj.CARBON_V1_NAME]["CARBON_CONTROLLER_CONTRACT"]

    # @staticmethod
    def initialize_contract_with_abi(self, address: str, abi: List[Any]) -> Contract:
        """
        Initialize a contract with an abi

        Parameters
        ----------
        w3 : Web3
            web3 instance
        address : str
            address of the contract
        abi : List[Any]
            abi of the contract

        """
        return self.ConfigObj.w3.eth.contract(address=address, abi=abi)

    # @staticmethod
    def initialize_contract_without_abi(self, address: str) -> Contract:
        """
        Initialize a contract without an abi

        Parameters
        ----------
        address : str
            address of the contract

        Returns
        -------
        Contract
            contract instance

        """
        abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={self.ConfigObj.ETHERSCAN_TOKEN}"
        _abi = json.loads(requests.get(abi_endpoint).text)
        return self.ConfigObj.w3.eth.contract(address=address, abi=_abi["result"])

    def initialize_contract(self, address: str, _abi: Any = None) -> Contract:
        """
        Initialize a contract with an abi

        Parameters
        ----------
        w3 : Web3
            web3 instance
        address : str
            address of the contract
        abi : List[Any]
            abi of the contract

        """

        if _abi is None:
            return self.initialize_contract_without_abi(address=address)
        else:
            return self.initialize_contract_with_abi(address=address, abi=_abi)

    def contract_from_address(self, exchange_name: str, pool_address: str) -> Contract:
        """
        Returns the contract for a given exchange and pool address

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool

        Returns
        -------
        Contract
            The contract for the pool

        """

        if exchange_name == self.ConfigObj.BANCOR_V2_NAME:
            return self.initialize_contract(
                address=self.ConfigObj.w3.toChecksumAddress(pool_address),
                _abi=abi.BANCOR_V2_CONVERTER_ABI,
            )
        elif exchange_name == self.ConfigObj.BANCOR_V3_NAME:
            return self.ConfigObj.BANCOR_NETWORK_INFO_CONTRACT
        elif exchange_name in self.ConfigObj.UNIV2_FORKS:
            return self.initialize_contract(
                address=self.ConfigObj.w3.toChecksumAddress(pool_address),
                _abi=abi.UNISWAP_V2_POOL_ABI,
            )
        elif exchange_name == self.ConfigObj.UNISWAP_V3_NAME:
            return self.initialize_contract(
                address=self.ConfigObj.w3.toChecksumAddress(pool_address),
                _abi=abi.UNISWAP_V3_POOL_ABI,
            )
        elif self.ConfigObj.CARBON_V1_NAME in exchange_name:

            return self.initialize_contract(
                address=self.ConfigObj.w3.toChecksumAddress(pool_address),
                _abi=abi.CARBON_CONTROLLER_ABI,
            )
        else:
            raise NotImplementedError(f"Exchange {exchange_name} not implemented")

    def get_or_init_contract(self, exchange_name: str, pool_address: str) -> Contract:
        """
        Returns whether a contract exists for a given exchange and pool address

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool

        Returns
        -------
        Contract
            The contract for the pool

        """

        if exchange_name not in self.contracts:
            self.contracts[exchange_name] = {}

        if pool_address not in self.contracts[exchange_name]:
            print(f"Initializing contract for {exchange_name} {pool_address}")
            self.contracts[exchange_name][pool_address] = self.contract_from_address(
                exchange_name, pool_address
            )

        return self.contracts[exchange_name][pool_address]

    def get_contract_for_exchange(
            self, exchange: str = None, pool_address: str = None, init_contract=True
    ) -> Contract:
        """
        Get the relevant ABI for the exchange

        Parameters
        ----------
        exchange : str
            exchange name
        pool_address : str
            pool address
        init_contract : bool
            whether to initialize the contract or not

        Returns
        -------
        Contract
            contract object

        """
        if exchange == self.ConfigObj.BANCOR_V2_NAME:
            return self.ConfigObj.w3.eth.contract(abi=_abi.BANCOR_V2_CONVERTER_ABI, address=pool_address)

        elif exchange == self.ConfigObj.BANCOR_V3_NAME:
            if init_contract:
                return self.ConfigObj.w3.eth.contract(
                    abi=_abi.BANCOR_V3_POOL_COLLECTION_ABI,
                    address=self.ConfigObj.w3.toChecksumAddress(self.ConfigObj.BANCOR_V3_POOL_COLLECTOR_ADDRESS),
                )
            else:
                return self.ConfigObj.BANCOR_NETWORK_INFO_CONTRACT

        elif exchange in self.ConfigObj.UNIV2_FORKS:
            return self.ConfigObj.w3.eth.contract(abi=_abi.UNISWAP_V2_POOL_ABI, address=pool_address)

        elif exchange == self.ConfigObj.UNISWAP_V3_NAME:
            return self.ConfigObj.w3.eth.contract(abi=_abi.UNISWAP_V3_POOL_ABI, address=pool_address)

        elif self.ConfigObj.CARBON_V1_NAME in exchange:
            return self.ConfigObj.CARBON_CONTROLLER_CONTRACT

    def get_filters_from_contract_and_exchange(self, exchange_name: str, contract: Contract) -> Any:
        """
        Returns the callable for the event filter for the given exchange

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        contract : Contract
            The exchange

        Returns
        -------
        Any
            The callable for the event filter
        """
        callables = []
        if self.ConfigObj.BANCOR_V2_NAME in exchange_name:
            callables.append(contract.events.TokenRateUpdate)
        elif self.ConfigObj.BANCOR_V3_NAME in exchange_name:
            callables.append(contract.events.TradingLiquidityUpdated)
        elif self.ConfigObj.UNISWAP_V2_NAME in exchange_name:
            callables.append(contract.events.Sync)
        elif self.ConfigObj.UNISWAP_V3_NAME in exchange_name:
            callables.append(contract.events.Swap)
        elif self.ConfigObj.SUSHISWAP_V2_NAME in exchange_name:
            callables.append(contract.events.Sync)
        elif self.ConfigObj.CARBON_V1_NAME in exchange_name:
            callables.extend(
                (
                    contract.events.StrategyCreated,
                    contract.events.StrategyUpdated,
                    contract.events.StrategyDeleted,
                )
            )
        return callables

    def get_event_filters(self, exchange_name: [str], contract: Contract, latest_block_for_exchange: int) -> Optional[
        List[Dict[str, Any]]]:
        """
        Creates a _filter for the relevant event for a given exchange

        Parameters
        ----------
        exchange_name: [str]
            The name of the exchange
        contract: Contract
            The exchange
        latest_block_for_exchange: int
            The latest block for the exchange

        Returns
        -------
        filters: [Dict[str, Any]]
            The list of filters for the relevant events
        """
        return [
            {
                "exchange": exchange_name,
                "filter": callable.createFilter(
                    fromBlock=latest_block_for_exchange, toBlock="latest"
                ),
            } for callable in self.get_filters_from_contract_and_exchange(exchange_name, contract)
        ]

    def get_carbon_pairs(self) -> List[Tuple[str, str]]:
        """
        Returns a list of all Carbon token pairs

        Returns
        -------
        List[Tuple[str, str]]
            A list of all Carbon token pairs

        """
        return self.carbon_controller.pairs().call()

    def get_strategies(self, pair: Tuple[str, str]) -> List[int]:
        """
        Returns a list of strategy ids for the specified pair

        Parameters
        ----------
        pair : Tuple[str, str]
            The token pair

        Returns
        -------
        List[int]
            A list of strategy ids for the specified pair
        """
        num_strategies = self.get_strategies_count_by_pair(pair[0], pair[1])
        print(f"Number of strategies for {pair[0]}-{pair[1]}: {num_strategies}")
        return self.get_strategies_by_pair(pair[0], pair[1], 0, num_strategies)

    def get_carbon_strategies(self):
        """
        Gets every Carbon Strategy
        """
        all_pairs = self.get_carbon_pairs()
        with brownie.multicall(address=self.c.MULTICALL_CONTRACT_ADDRESS):
            strats = [strategy for pair in all_pairs for strategy in self.get_strategies(pair)]
        return strats

    def get_carbon_strategy(self, strategy_id: int) -> Tuple[str, str, str, str, str, str, str]:
        """
        Returns a tuple of the strategy's data

        Parameters
        ----------
        strategy_id : int
            The id of the strategy

        Returns
        -------
        Tuple[str, str, str, str, str, str, str]
            A tuple of the strategy's data
        """
        return self.carbon_controller.strategy(strategy_id)

    def get_strategies_count_by_pair(self, token0: str, token1: str) -> int:
        """
        Returns the number of strategies in the specified token pair

        Parameters
        ----------
        token0 : str
            The token address of the first token
        token1 : str
            The token address of the second token

        Returns
        -------
        int
            The number of strategies in the specified token pair
        """
        try:
            return self.carbon_controller.strategiesByPairCount(token0, token1).call()
        except Exception as e:
            self.c.logger.error(f"Error getting strategies count by pair:{token0}, {token1}, {e}, skipping...")
            return 0

    def get_strategies_by_pair(
            self, token0: str, token1: str, start_idx: int, end_idx: int
    ) -> List[int]:
        """
        Returns a list of strategy ids for the specified pair, given a start and end index

        Parameters
        ----------
        token0 : str
            The token address of the first token
        token1 : str
            The token address of the second token
        start_idx : int
            The start index
        end_idx : int
            The end index

        Returns
        -------
        List[int]
            A list of strategy ids for the specified pair, given a start and end index
        """
        if end_idx == 0:
            end_idx = 5000
        try:
            return self.carbon_controller.strategiesByPair(token0, token1, start_idx, end_idx).call()
        except Exception as e:
            self.c.logger.error(f"[contract_helper] Error getting strategies by pair:{token0}, {token1}, {e}, skipping...")
            return []
