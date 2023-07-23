# coding=utf-8
"""
Contains the base class for the managers modules.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Type, Optional, Tuple

import brownie
from web3 import Web3
from web3.contract import Contract

from fastlane_bot import Config
from fastlane_bot.events.exchanges import exchange_factory
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
    """

    web3: Web3
    cfg: Config
    pool_data: List[Dict[str, Any]]
    alchemy_max_block_fetch: int
    event_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    pool_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    erc20_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    exchanges: Dict[str, Exchange] = field(default_factory=dict)
    uniswap_v2_event_mappings: Dict[str, str] = field(default_factory=dict)
    unmapped_uni2_events: List[str] = field(default_factory=list)
    tokens: List[Dict[str, str]] = field(default_factory=dict)

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

    def __post_init__(self):
        for exchange_name in self.SUPPORTED_EXCHANGES:
            self.exchanges[exchange_name] = exchange_factory.get_exchange(exchange_name)
        self.init_exchange_contracts()

    @staticmethod
    def exchange_name_from_event(event: Dict[str, Any]) -> str:
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
        return next(
            (
                exchange_name
                for exchange_name, pool_class in pool_factory._creators.items()
                if pool_class.event_matches_format(event)
            ),
            None,
        )

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
            self.web3.toChecksumAddress(address),
        )
        return tkns or (None, None)

    def multicall(self, address):
        return brownie.multicall(address)

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
            start_time = time.time()
            self.cfg.logger.info("Updating carbon pools w/ multicall...")

            # Create a CarbonController contract object
            carbon_controller = brownie.Contract.from_abi(
                address=self.cfg.CARBON_CONTROLLER_ADDRESS,
                abi=self.exchanges["carbon_v1"].get_abi(),
                name="CarbonController",
            )

            # Store the contract object in pool_contracts
            self.pool_contracts["carbon_v1"][
                self.cfg.CARBON_CONTROLLER_ADDRESS
            ] = carbon_controller

            # Create a list of pairs from the CarbonController contract object
            pairs = [(second, first) for first, second in carbon_controller.pairs()]

            # Create a reversed list of pairs
            pairs_reverse = [(second, first) for first, second in pairs]

            # Combine both pair lists and add extra parameters
            all_pairs = [(pair[0], pair[1], 0, 5000) for pair in pairs]

            strategies_by_pair = self.get_strats_by_pair(all_pairs, carbon_controller)

            # expand strategies_by_pair
            strategies_by_pair = [
                s for strat in strategies_by_pair if strat for s in strat if s
            ]

            # Log the time taken for the above operations
            self.cfg.logger.info(
                f"Fetched {len(strategies_by_pair)} carbon strategies in {time.time() - start_time} seconds"
            )

            start_time = time.time()
            current_block = self.web3.eth.blockNumber

            # Create pool info for each strategy
            for strategy in strategies_by_pair:
                if len(strategy) > 0:
                    self.add_pool_info_from_event(
                        strategy=strategy, block_number=current_block
                    )

            # Log the time taken for the above operations
            self.cfg.logger.info(
                f"Updated {len(strategies_by_pair)} carbon strategies info in {time.time() - start_time} seconds"
            )

        return [
            i
            for i, pool_info in enumerate(self.pool_data)
            if pool_info["last_updated_block"]
            < update_from_contract_block - self.alchemy_max_block_fetch
        ]

    def get_strats_by_pair(self, all_pairs, carbon_controller):
        with self.multicall(address=self.cfg.MULTICALL_CONTRACT_ADDRESS):
            # Fetch strategies for each pair from the CarbonController contract object
            strategies_by_pair = [
                carbon_controller.strategiesByPair(*pair) for pair in all_pairs
            ]
        return strategies_by_pair

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
            return record["symbol"], int(record["decimals"])

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
            pool_info = self.add_pool_info_from_contract(
                address=addr, event=event, block_number=event["blockNumber"]
            )

        if addr == self.cfg.CARBON_CONTROLLER_ADDRESS:
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
        if ex_name == "carbon_v1":
            return "cid", event["args"]["id"]
        if ex_name in {"uniswap_v2", "sushiswap_v2", "uniswap_v3"}:
            return "address", addr
        if ex_name == "bancor_v3":
            value = (
                event["args"]["tkn_address"]
                if event["args"]["tkn_address"] != self.cfg.BNT_ADDRESS
                else event["args"]["pool"]
            )
            return "tkn1_address", value

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
