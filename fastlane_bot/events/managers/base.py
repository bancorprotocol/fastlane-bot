# coding=utf-8
"""
Contains the base class for the managers modules.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Type, Optional, Tuple

import pandas as pd
from web3 import Web3, AsyncWeb3
from web3.contract import Contract

from fastlane_bot import Config
from fastlane_bot.config.multicaller import MultiCaller
from fastlane_bot.events.exchanges import exchange_factory, SolidlyV2
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools import pool_factory


@dataclass
class BaseManager:
    """
    The Base class is responsible for coordinating the data fetching process.

    Parameters
    ----------
    web3 : Web3
        The Web3 instance.
    cfg : Config
        The Config instance.
    pool_data : List[Dict[str, Any]]
        The pool data.
    alchemy_max_block_fetch : int
        The maximum number of blocks to fetch from Alchemy.
    event_contracts : Dict[str, Contract or Type[Contract]]
        The event contracts.
    pool_contracts : Dict[str, Contract or Type[Contract]]
        The pool contracts.
    erc20_contracts : Dict[str, Contract or Type[Contract]]
        The ERC20 contracts.
    exchanges : Dict[str, Exchange]
        The exchanges.
    uniswap_v2_event_mappings : Dict[str, str]
        The UniswapV2 event mappings.
    unmapped_uni2_events : List[str]
        The unmapped UniswapV2 events.
    tokens : List[Dict[str, str]]
        The tokens.
    TOKENS_MAPPING : Dict[str, Any]
        The tokens mapping.
    SUPPORTED_EXCHANGES : Dict[str, Any]
        The supported exchanges.
    read_only : bool
        Whether the bot is running in read only mode.
    """

    web3: Web3
    w3_async: AsyncWeb3
    cfg: Config
    pool_data: List[Dict[str, Any]]
    alchemy_max_block_fetch: int
    tenderly_event_contracts: Dict[str, Contract or Type[Contract]] = field(
        default_factory=dict
    )
    tenderly_event_exchanges: List[str] = field(default_factory=list)
    w3_tenderly: Web3 = None
    event_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    pool_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    token_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    erc20_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    exchanges: Dict[str, Exchange] = field(default_factory=dict)
    factory_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    uniswap_v2_event_mappings: Dict[str, str] = field(default_factory=dict)
    uniswap_v3_event_mappings: Dict[str, str] = field(default_factory=dict)
    solidly_v2_event_mappings: Dict[str, str] = field(default_factory=dict)
    unmapped_uni2_events: List[str] = field(default_factory=list)
    tokens: List[Dict[str, str]] = field(default_factory=dict)
    target_tokens: List[str] = field(default_factory=list)
    tenderly_fork_id: str = None
    pools_to_add_from_contracts: List[Tuple[str, str, Any, str, str]] = field(
        default_factory=list
    )
    blockchain: str = None
    TOKENS_MAPPING: Dict[str, Any] = field(
        default_factory=lambda: {
            "ETH_ADDRESS": ("ETH", 18),
            "WETH_ADDRESS": ("WETH", 18),
            "WBTC_ADDRESS": ("WBTC", 8),
            "BNT_ADDRESS": ("BNT", 18),
            "USDC_ADDRESS": ("USDC", 6),
        }
    )

    SUPPORTED_EXCHANGES: List[str] = None
    SUPPORTED_BASE_EXCHANGES: List[str] = None
    _fee_pairs: Dict[Tuple[str, str], int] = field(default_factory=dict)
    carbon_inititalized: bool = None
    replay_from_block: int = None

    forked_exchanges: List[str] = field(default_factory=list)
    static_pools: Dict[str, List[str]] = field(default_factory=dict)

    prefix_path: str = ""
    read_only: bool = False

    def __post_init__(self):
        initialized_exchanges = []
        self.SUPPORTED_BASE_EXCHANGES = []
        for exchange_name in self.SUPPORTED_EXCHANGES:
            initialize_events = False
            base_exchange_name = self.cfg.network.exchange_name_base_from_fork(exchange_name=exchange_name)
            if exchange_name in ["pancakeswap_v2", "pancakeswap_v3", "velocimeter_v2"]:
                initialize_events = True
            elif base_exchange_name not in initialized_exchanges:
                initialize_events = True
                initialized_exchanges.append(base_exchange_name)

            if base_exchange_name not in self.SUPPORTED_BASE_EXCHANGES:
                self.SUPPORTED_BASE_EXCHANGES.append(base_exchange_name)
            self.exchanges[exchange_name] = exchange_factory.get_exchange(key=exchange_name, cfg=self.cfg, exchange_initialized=initialize_events)
            if base_exchange_name in "solidly_v2":
                self.exchanges[exchange_name] = self.handle_solidly_exchanges(exchange=self.exchanges[exchange_name])

        self.init_exchange_contracts()
        self.set_carbon_v1_fee_pairs()
        self.init_tenderly_event_contracts()


    def handle_solidly_exchanges(self, exchange):
        """
        Handles getting stable & volatile fees for Solidly forks
        """
        exchange_name = exchange.exchange_name
        self.factory_contracts[exchange_name] = self.w3_async.eth.contract(
            address=self.cfg.FACTORY_MAPPING[exchange_name],
            abi=exchange.get_factory_abi,
        )
        exchange.factory_contract = self.factory_contracts[exchange.exchange_name]

        return exchange

    @property
    def fee_pairs(self) -> Dict[Tuple[str, str], int]:
        """
        Get the fee pairs.

        Returns
        -------
        Dict[Tuple[str, str], int]
            The fee pairs.

        """
        return self._fee_pairs

    @fee_pairs.setter
    def fee_pairs(self, value: Dict[Tuple[str, str], int]):
        """
        Set the fee pairs.

        Parameters
        ----------
        value : Dict[Tuple[str, str], int]
            The fee pairs.

        """
        self._fee_pairs = value

    def set_carbon_v1_fee_pairs(self):
        """
        Set the carbon v1 fee pairs.
        """
        if "carbon_v1" in self.exchanges:
            # Create or get CarbonController contract object
            carbon_controller = self.create_or_get_carbon_controller()

            # Get pairs by contract
            pairs = self.get_carbon_pairs(carbon_controller)

            # Get the fee for each pair
            fee_pairs = self.get_fee_pairs(pairs, carbon_controller)

            # Set the fee pairs
            self.exchanges["carbon_v1"].fee_pairs = fee_pairs

    def get_fee_pairs(
        self, all_pairs: List[Tuple[str, str, int, int]], carbon_controller: Contract
    ) -> Dict[Tuple[str, str], int]:
        """
        Get the fees for each pair and store in a dictionary.

        Parameters
        ----------
        all_pairs : List[Tuple]
            A list of pairs.
        carbon_controller : Contract
            The CarbonController contract object.

        Returns
        -------
        Dict[Tuple[str, str], int]
            A dictionary of fees for each pair.
        """
        # Get the fees for each pair and store in a dictionary
        fees_by_pair = self.get_fees_by_pair(all_pairs, carbon_controller)
        fee_pairs = {
            (
                self.web3.to_checksum_address(pair[0]),
                self.web3.to_checksum_address(pair[1]),
            ): fee
            for pair, fee in zip(all_pairs, fees_by_pair)
        }
        # Add the reverse pair to the fee_pairs dictionary
        fee_pairs.update(
            {
                (
                    self.web3.to_checksum_address(pair[1]),
                    self.web3.to_checksum_address(pair[0]),
                ): fee
                for pair, fee in zip(all_pairs, fees_by_pair)
            }
        )
        return fee_pairs

    def exchange_name_from_event(self, event: Dict[str, Any]) -> str:
        """
        Get the exchange name from the event.

        Parameters
        ----------
        event : Dict[str, Any]
            The event.

        Returns
        -------
        str
            The exchange name.
        """

        for exchange_name, pool_class in pool_factory._creators.items():
            for _ex_name in self.SUPPORTED_EXCHANGES:
                if exchange_name not in self.cfg.network.exchange_name_base_from_fork(_ex_name):
                    continue
                if pool_class.event_matches_format(event, self.static_pools, exchange_name=_ex_name):
                    return _ex_name
        return None

    def check_forked_exchange_names(
        self, exchange_name_default: str = None, address: str = None, event: Any = None
    ) -> str:
        """
        Check the forked exchange names. If the exchange name is forked (Sushiswap from UniswapV2, etc) return the
        real exchange name.

        Parameters
        ----------
        exchange_name_default : str, optional
            The default exchange name.
        address : str, optional
            The address.
        event : Any, optional
            The event.

        Returns
        -------
        str
            The real exchange name.

        """
        if exchange_name_default is None:
            exchange_name_default = self.exchange_name_from_event(event)

        return exchange_name_default

    def get_tkn_info(self, address: str) -> Tuple[Optional[str], Optional[int]]:
        """
        Get the token info.

        Parameters
        ----------
        address : str
            The address.

        Returns
        -------
        Tuple[Optional[str], Optional[int]]
            The token info.

        """
        tkns = self.get_tkn_symbol_and_decimals(
            self.web3,
            self.erc20_contracts,
            self.cfg,
            self.web3.to_checksum_address(address),
        )
        return tkns or (None, None)

    def get_rows_to_update(self, update_from_contract_block: int) -> List[int]:
        """
        Get the rows to update.

        Parameters
        ----------
        update_from_contract_block : int
            The latest block number to update from.

        Returns
        -------
        List[int]
            The rows to update.

        """

        if "carbon_v1" in self.SUPPORTED_EXCHANGES:
            self.update_carbon(update_from_contract_block)

        return [
            i
            for i, pool_info in enumerate(self.pool_data)
            if pool_info["last_updated_block"]
            < update_from_contract_block - self.alchemy_max_block_fetch
        ]

    def update_carbon(self, current_block: int):
        """
        Update the carbon pools.

        Parameters
        ----------
        current_block : int
            The current block number.

        Returns
        -------
        List[int]
            The rows to update.

        """
        start_time = time.time()
        self.cfg.logger.info(
            "[events.managers.base] Updating carbon pools w/ multicall..."
        )

        # Create or get CarbonController contract object
        carbon_controller = self.create_or_get_carbon_controller()

        # Create a list of pairs from the CarbonController contract object
        pairs = self.get_carbon_pairs(carbon_controller, self.target_tokens)

        # Create a list of strategies for each pair
        strategies_by_pair = self.get_strategies(pairs, carbon_controller)

        # Get the fee for each pair
        if not self.fee_pairs:
            # Log that the fee pairs are being set
            self.cfg.logger.debug("[events.managers.base] Setting carbon fee pairs...")
            self.fee_pairs = self.get_fee_pairs(pairs, carbon_controller)

        # Log the time taken for the above operations
        self.cfg.logger.debug(
            f"Fetched {len(strategies_by_pair)} carbon strategies in {time.time() - start_time} seconds"
        )

        start_time = time.time()

        # Create pool info for each strategy
        for strategy in strategies_by_pair:
            if len(strategy) > 0:
                self.exchanges["carbon_v1"].save_strategy(
                    strategy=strategy,
                    block_number=current_block,
                    cfg=self.cfg,
                    func=self.add_pool_info,
                    carbon_controller=carbon_controller,
                )

        # Log the time taken for the above operations
        self.cfg.logger.debug(
            f"Updated {len(strategies_by_pair)} carbon strategies info in {time.time() - start_time} seconds"
        )

    def get_carbon_pairs(
        self, carbon_controller: Contract, target_tokens: List[str] = None
    ) -> List[Tuple[str, str, int, int]]:
        """
        Get the carbon pairs.

        Parameters
        ----------
        carbon_controller : Contract
            The CarbonController contract object.
        target_tokens : List[str], optional
            The target tokens, by default None

        Returns
        -------
        List[Tuple[str, str, int, int]]
            The carbon pairs.

        """
        pairs = (
            self.get_carbon_pairs_by_state()
            if self.carbon_inititalized
            else self.get_carbon_pairs_by_contract(carbon_controller)
        )
        # Log whether the carbon pairs were retrieved from the state or the contract
        self.cfg.logger.debug(
            f"Retrieved {len(pairs)} carbon pairs from {'state' if self.carbon_inititalized else 'contract'}"
        )
        if target_tokens is None or target_tokens == []:
            target_tokens = []
            for pair in pairs:
                if pair[0] not in target_tokens:
                    target_tokens.append(pair[0])
                if pair[1] not in target_tokens:
                    target_tokens.append(pair[1])
        return [
            (pair[0], pair[1], 0, 5000)
            for pair in pairs
            if pair[0] in target_tokens and pair[1] in target_tokens
        ]

    @staticmethod
    def get_carbon_pairs_by_contract(
        carbon_controller: Contract, replay_from_block: int or str = None
    ) -> List[Tuple[str, str]]:
        """
        Get the carbon pairs by contract.

        Parameters
        ----------
        carbon_controller : Contract
            The CarbonController contract object.
        replay_from_block : int or str, optional
            The block number to replay from, by default 'latest'

        Returns
        -------
        List[Tuple[str, str]]
            The carbon pairs.

        """
        return [
            (second, first)
            for first, second in carbon_controller.functions.pairs().call(
                block_identifier=replay_from_block or "latest"
            )
        ]

    def get_carbon_pairs_by_state(self) -> List[Tuple[str, str]]:
        """
        Get the carbon pairs by state.

        Returns
        -------
        List[Tuple[str, str]]
            The carbon pairs.

        """
        return [
            (p["tkn0_address"], p["tkn1_address"])
            for p in self.pool_data
            if p["exchange_name"] == "carbon_v1"
        ]

    def create_or_get_carbon_controller(self):
        """
        Create or get the CarbonController contract object.

        Returns
        -------
        carbon_controller : Contract
            The CarbonController contract object.

        """
        if (
            self.cfg.CARBON_CONTROLLER_ADDRESS in self.pool_contracts["carbon_v1"]
            and not self.replay_from_block
        ):
            return self.pool_contracts["carbon_v1"][self.cfg.CARBON_CONTROLLER_ADDRESS]

        # Create a CarbonController contract object
        carbon_controller = self.cfg.w3.eth.contract(
            address=self.cfg.CARBON_CONTROLLER_ADDRESS,
            abi=self.exchanges["carbon_v1"].get_abi(),
        )

        # Store the contract object in pool_contracts
        self.pool_contracts["carbon_v1"][
            self.cfg.CARBON_CONTROLLER_ADDRESS
        ] = carbon_controller
        return carbon_controller

    def get_strats_by_contract(
        self,
        pairs: List[Tuple[str, str, int, int]],
        carbon_controller: Contract,
    ) -> List[List[Any]]:
        """
        Get the strategies by contract.

        Parameters
        ----------
        pairs : List[Tuple[str, str, int, int]]
            The pairs.
        carbon_controller : Contract
            The CarbonController contract object.

        Returns
        -------
        List[List[str]]
            The strategies.

        """
        multicaller = MultiCaller(
            contract=carbon_controller,
            block_identifier=self.replay_from_block or "latest",
            multicall_address=self.cfg.MULTICALL_CONTRACT_ADDRESS,
            web3=self.web3
        )

        with multicaller as mc:
            for pair in pairs:
                try:
                    # Loading the strategies for each pair without executing the calls yet
                    mc.add_call(
                        carbon_controller.functions.strategiesByPair,
                        pair[0],
                        pair[1],
                        pair[2],
                        pair[3],
                    )
                except ValueError:
                    print(f"Error fetching strategiesByPair {pair}")

            # Fetch strategies for each pair from the CarbonController contract object
            strategies_by_pair = mc.multicall()

        self.carbon_inititalized = True

        # Log that Carbon is initialized
        self.cfg.logger.debug(
            f"[events.managers.base] Carbon is initialized {self.carbon_inititalized}"
        )
        self.cfg.logger.debug(
            f"[events.managers.base] Retrieved {len(strategies_by_pair)} carbon strategies"
        )
        return [s for strat in strategies_by_pair if strat for s in strat if s]

    def get_strats_by_state(self, pairs: List[List[Any]]) -> List[List[int]]:
        """
        Get the strategies by state.

        Parameters
        ----------
        pairs : List[Tuple[str, str, int, int]]
            The pairs.

        Returns
        -------
        List[List[Any]]
            The strategies retrieved from the state.

        """
        cids = [
            pool["cid"]
            for pool in self.pool_data
            if pool["exchange_name"] == "carbon_v1"
            and (pool["tkn0_address"], pool["tkn1_address"]) in pairs
            or (pool["tkn1_address"], pool["tkn0_address"]) in pairs
        ]
        strategies = []
        for cid in cids:
            pool_data = [pool for pool in self.pool_data if pool["cid"] == cid][0]

            # Constructing the orders based on the values from the pool_data dictionary
            order0 = [
                pool_data["y_0"],
                pool_data["z_0"],
                pool_data["A_0"],
                pool_data["B_0"],
            ]
            order1 = [
                pool_data["y_1"],
                pool_data["z_1"],
                pool_data["A_1"],
                pool_data["B_1"],
            ]

            # Fetching token addresses and converting them
            tkn0_address, tkn1_address = pool_data["tkn0"], pool_data["tkn1"]

            # Reconstructing the strategy object
            strategy = [cid, None, [tkn0_address, tkn1_address], [order0, order1]]

            # Appending the strategy to the list of strategies
            strategies.append(strategy)

        return strategies

    def get_strategies(
        self, pairs: List[Tuple[str, str, int, int]], carbon_controller: Contract
    ) -> List[List[str]]:
        """
        Get the strategies.

        Parameters
        ----------
        pairs : List[Tuple[str, str, int, int]]
            The pairs.
        carbon_controller : Contract
            The CarbonController contract object.

        Returns
        -------
        List[List[str]]
            The strategies.

        """
        # Log whether the carbon strats were retrieved from the state or the contract
        self.cfg.logger.debug(
            f"Retrieving carbon strategies from {'state' if self.carbon_inititalized else 'contract'}"
        )
        return (
            self.get_strats_by_state(pairs)
            if self.carbon_inititalized
            else self.get_strats_by_contract(pairs, carbon_controller)
        )

    def get_fees_by_pair(
        self, all_pairs: List[Tuple[str, str]], carbon_controller: Contract
    ):
        """
        Get the fees by pair.

        Parameters
        ----------
        all_pairs : List[Tuple[str, str]]
            The pairs.
        carbon_controller : Contract
            The carbon controller contract object.

        Returns
        -------
        List[int]
            The fees by pair.

        """
        multicaller = MultiCaller(
            contract=carbon_controller,
            block_identifier=self.replay_from_block or "latest",
            multicall_address=self.cfg.MULTICALL_CONTRACT_ADDRESS,
            web3=self.web3
        )

        with multicaller as mc:
            for pair in all_pairs:
                mc.add_call(
                    carbon_controller.functions.pairTradingFeePPM, pair[0], pair[1]
                )

        return multicaller.multicall()

    def get_tkn_symbol_and_decimals(
        self, web3: Web3, erc20_contracts: Dict[str, Contract], cfg: Config, addr: str
    ) -> Tuple[str, int]:
        """
        Get the token symbol and decimals.

        Parameters
        ----------
        web3 : Web3
            The web3 instance.
        erc20_contracts : Dict[str, Contract]
            The erc20 contracts.
        cfg : Config
            The config.
        addr : str
            The address.

        Returns
        -------
        Tuple[str, int]
            The token symbol and decimals.

        """
        token_info = self.get_token_info_from_config(cfg, addr)
        if token_info:
            return token_info

        record = next((add for add in self.tokens if add["address"] == addr), None)
        if record:
            return record["symbol"], int(float(record["decimals"]))

        return self.get_token_info_from_contract(web3, erc20_contracts, addr)

    def get_token_info_from_config(
        self, cfg: Config, addr: str
    ) -> Optional[Tuple[str, int]]:
        """
        Get the token info from config.

        Parameters
        ----------
        cfg : Config
            The config.
        addr : str
            The address.

        Returns
        -------
        Optional[Tuple[str, int]]
            The token info.

        """
        return next(
            (
                info
                for address_attr, info in self.TOKENS_MAPPING.items()
                if addr in [getattr(cfg, address_attr)]
            ),
            None,
        )

    def validate_pool_info(
        self,
        addr: Optional[str] = None,
        event: Optional[Dict[str, Any]] = None,
        pool_info: Optional[Dict[str, Any]] = None,
        key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Validate the pool info.

        Parameters
        ----------
        addr : Optional[str], optional
            The address, by default None
        event : Optional[Dict[str, Any]], optional
            The event, by default None
        pool_info : Optional[Dict[str, Any]], optional
            The pool info, by default None
        key : Optional[str], optional
            The key, by default None
        block_number : Optional[int], optional
            The block number, by default None

        Returns
        -------
        Optional[Dict[str, Any]]
            The pool info.

        """
        if key != "cid" and (pool_info is None or not pool_info):
            # Uses method in ContractsManager.add_pool_info_from_contract class to get pool info from contract
            pool_info = self.add_pool_info_from_contract(
                address=addr, event=event, block_number=event["blockNumber"]
            )

        if addr in self.cfg.CARBON_CONTROLLER_MAPPING:
            cid = event["args"]["id"] if event is not None else pool_info["cid"]
            for pool in self.pool_data:
                if pool["cid"] == cid:
                    pool_info = pool
                    break

        if isinstance(pool_info, float):
            return

        return pool_info

    def get_key_and_value(
        self, event: Dict[str, Any], addr: str, ex_name: str
    ) -> Tuple[str, Any]:
        """
        Get the key and value.

        Parameters
        ----------
        event : Dict[str, Any]
            The event.
        addr : str
            The address.
        ex_name : str
            The exchange name.

        Returns
        -------
        Tuple[str, Any]
            The key and value.

        """
        if ex_name == "bancor_pol":
            return "token", event["args"]["token"]
        if ex_name in self.cfg.CARBON_V1_FORKS:
            return "cid", event["args"]["id"]
        if ex_name in self.cfg.ALL_FORK_NAMES_WITHOUT_CARBON:
            return "address", addr
        if ex_name == "bancor_v2":
            return ("tkn0_address", "tkn1_address"), (
                event["args"]["_token1"],
                event["args"]["_token2"],
            )
        if ex_name == "bancor_v3":
            value = (
                event["args"]["tkn_address"]
                if event["args"]["tkn_address"] != self.cfg.BNT_ADDRESS
                else event["args"]["pool"]
            )
            return "tkn1_address", value
        raise ValueError(
            f"[managers.base.get_key_and_value] Exchange {ex_name} not supported"
        )

    def handle_strategy_deleted(self, event: Dict[str, Any]) -> None:
        """
        Handle the strategy deleted event.

        Parameters
        ----------
        event : Dict[str, Any]
            The event.
        """
        cid = event["args"]["id"]
        self.pool_data = [p for p in self.pool_data if p["cid"] != cid]
        self.exchanges["carbon_v1"].delete_strategy(event["args"]["id"])

    def deduplicate_pool_data(self) -> None:
        """
        Deduplicate the pool data.
        """
        self.pool_data = sorted(
            self.pool_data, key=lambda x: x["last_updated_block"], reverse=True
        )
        seen = set()
        no_duplicates = [
            d for d in self.pool_data if d["cid"] not in seen and not seen.add(d["cid"])
        ]
        self.pool_data = no_duplicates

    @staticmethod
    def pool_key_value_from_event(key: str, event: Dict[str, Any]) -> Any:
        """
        Get the pool key value from the event.

        Parameters
        ----------
        key : str
            The key.
        event : Dict[str, Any]
            The event.

        Returns
        -------
        Any
            The pool key value.
        """
        if key == "cid":
            return event["args"]["id"]
        elif key == "address":
            return event["address"]
        elif key == "tkn0_address":
            return event["args"]["token0"]
        elif key == "tkn1_address":
            return event["args"]["token1"]

    print_events = []

    def get_bancor_pol_pools(self, current_block: int):
        """
        Update the Bancor Pol pools.

        Parameters
        ----------
        current_block : int
            The current block number.

        Returns
        -------
        List[int]
            The rows to update.

        """
        start_time = time.time()
        self.cfg.logger.info("[events.managers.base] Updating Bancor POL pools...")

        # Create or get CarbonController contract object
        bancor_pol = self.create_or_get_bancor_pol_contract()

        trading_enable_events = bancor_pol.events.TradingEnabled.get_logs(
            fromBlock=self.cfg.BANCOR_POL_START_BLOCK
        )

        # Create pool info for each token
        for event in trading_enable_events:
            self.exchanges["bancor_pol"].save_strategy(
                token=event[0],
                block_number=current_block,
                cfg=self.cfg,
                func=self.add_pool_info,
            )

    def create_or_get_bancor_pol_contract(self):
        """
        Create or get the BancorPol contract object.

        Returns
        -------
        bancor_pol : Contract
            The Bancor Pol contract object.

        """
        if (
            self.cfg.BANCOR_POL_ADDRESS in self.pool_contracts["bancor_pol"]
            and not self.replay_from_block
        ):
            return self.pool_contracts["bancor_pol"][self.cfg.BANCOR_POL_ADDRESS]

        # Create a CarbonController contract object
        bancor_pol = self.cfg.w3.eth.contract(
            address=self.cfg.BANCOR_POL_ADDRESS,
            abi=self.exchanges["bancor_pol"].get_abi(),
        )

        # Store the contract object in pool_contracts
        self.pool_contracts["bancor_pol"][self.cfg.BANCOR_POL_ADDRESS] = bancor_pol
        return bancor_pol
