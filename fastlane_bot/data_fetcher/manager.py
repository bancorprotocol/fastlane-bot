import random
import time
from dataclasses import field, dataclass
from typing import Dict, Any, List, Type, Optional, Callable, Tuple

import brownie
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.config import Config
from fastlane_bot.data.abi import ERC20_ABI, BANCOR_V3_NETWORK_INFO_ABI
from fastlane_bot.data_fetcher.exchanges import exchange_factory, Exchange
from fastlane_bot.data_fetcher.pools import Pool, pool_factory


@dataclass
class Manager:
    """
    The Manager class is responsible for coordinating the data fetching process.

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

    TOKENS_MAPPING: Dict[str, Any] = field(default_factory=lambda : {
        "ETH_ADDRESS": ("ETH", 18),
        "WETH_ADDRESS": ("WETH", 18),
        "WBTC_ADDRESS": ("WBTC", 8),
        "BNT_ADDRESS": ("BNT", 18),
        "USDC_ADDRESS": ("USDC", 6),
    })

    SUPPORTED_EXCHANGES: List[str] = None

    def __post_init__(self):
        for exchange_name in self.SUPPORTED_EXCHANGES:
            self.exchanges[exchange_name] = exchange_factory.get_exchange(exchange_name)
        self.init_exchange_contracts()

    def init_exchange_contracts(self):
        """
        Initialize the exchange contracts.
        """
        for exchange_name in self.SUPPORTED_EXCHANGES:
            self.event_contracts[exchange_name] = self.web3.eth.contract(
                abi=self.exchanges[exchange_name].get_abi(),
            )
            self.pool_contracts[exchange_name] = {}
            if exchange_name == "bancor_v3":
                self.pool_contracts[exchange_name][self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS] = brownie.Contract.from_abi(
                    address=self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS,
                    abi=BANCOR_V3_NETWORK_INFO_ABI,
                    name="BancorNetwork",
                )

    @staticmethod
    def get_or_create_token_contracts(
            web3: Web3, erc20_contracts: Dict[str, Contract], address: str
    ) -> Contract:
        """
        Get or create the token contracts.

        Parameters
        ----------
        web3 : Web3
            The Web3 instance.
        erc20_contracts : Dict[str, Contract]
            The ERC20 contracts.
        address : str
            The address.

        Returns
        -------
        Contract
            The token contract.

        """
        if address in erc20_contracts:
            contract = erc20_contracts[address]
        else:
            contract = web3.eth.contract(address=address, abi=ERC20_ABI)
            erc20_contracts[address] = contract
        return contract

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
                if pool_class.event_matches_format(event["args"])
            ),
            None,
        )

    @staticmethod
    def pool_type_from_exchange_name(exchange_name: str) -> Callable:
        """
        Get the pool type from the exchange name.

        Parameters
        ----------
        exchange_name : str
            The exchange name.

        Returns
        -------
        Callable
            The pool type class.

        """
        return pool_factory.get_pool(exchange_name)

    @staticmethod
    def pool_descr_from_info(pool_info: Dict[str, Any]) -> str:
        """
        Get the pool description from the pool info.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        Returns
        -------
        str
            The pool description.

        """
        return (
            f"{pool_info['exchange_name']} {pool_info['pair_name']} {pool_info['fee']}"
        )

    @staticmethod
    def pool_cid_from_descr(web3: Web3, descr: str) -> str:
        """
        Get the pool CID from the description. Only used for non-Carbon pools.

        Parameters
        ----------
        web3 : Web3
            The Web3 instance.
        descr : str
            The description.

        Returns
        -------
        str
            The pool CID.

        """
        return web3.keccak(text=descr).hex()

    @property
    def events(self) -> List[Type[Contract]]:
        """
        Get the events from the exchanges.

        Returns
        -------
        List[Type[Contract]]
            The events.
        """
        return [
            event
            for exchange in self.exchanges.values()
            for event in exchange.get_events(
                self.event_contracts[exchange.exchange_name]
            )
        ]

    @property
    def pools(self) -> List[Pool]:
        """
        Get the pools from the exchanges.

        Returns
        -------
        List[Pool]
            The pools from the exchanges.
        """
        return [
            pool
            for exchange in self.exchanges.values()
            for pool in exchange.get_pools()
        ]

    def add_pool_info_from_strategy(self, strategy: List[Any]) -> Dict[str, Any]:
        """
        Add the pool info from the strategy.

        Parameters
        ----------
        strategy : List[Any]
            The strategy.

        Returns
        -------
        Dict[str, Any]
            The pool info.

        """
        cid = strategy[0]
        order0, order1 = strategy[3][0], strategy[3][1]
        tkn0_address, tkn1_address = self.web3.toChecksumAddress(
            strategy[2][0]
        ), self.web3.toChecksumAddress(strategy[2][1])

        return self.add_pool_info(
            address=self.cfg.CARBON_CONTROLLER_ADDRESS,
            exchange_name="carbon_v1",
            fee="0.002",
            fee_float=0.002,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
            cid=cid,
            other_args=dict(
                y_0=order0[0],
                y_1=order1[0],
                z_0=order0[1],
                z_1=order1[1],
                A_0=order0[2],
                A_1=order1[2],
                B_0=order0[3],
                B_1=order1[3],
            ),
        )

    def add_pool_info_from_contract(self, exchange_name: str = None, address: str = None, event: Any = None) -> Dict[str, Any]:
        """
        Add the pool info from the contract.

        Parameters
        ----------
        exchange_name : str, optional
            The exchange name.
        address : str, optional
            The address.
        event : Any, optional
            The event.

        Returns
        -------
        Dict[str, Any]
            The pool info from the contract.

        """
        exchange_name = self.check_forked_exchange_names(exchange_name, address, event)
        if not exchange_name:
            print(f"Exchange name not found {event}")
            return None

        pool_contract = self.get_pool_contract(exchange_name, address)
        self.pool_contracts[exchange_name][address] = pool_contract
        fee, fee_float = self.exchanges[exchange_name].get_fee(address, pool_contract)

        t0_addr = self.exchanges[exchange_name].get_tkn0(address, pool_contract, event)
        t1_addr = self.exchanges[exchange_name].get_tkn1(address, pool_contract, event)

        return self.add_pool_info(
            address=address,
            exchange_name=exchange_name,
            fee=fee,
            fee_float=fee_float,
            tkn0_address=t0_addr,
            tkn1_address=t1_addr,
            cid=event["args"]["id"] if exchange_name == "carbon_v1" else None,
            contract=pool_contract,
        )

    def check_forked_exchange_names(self, exchange_name_default: str = None, address: str = None, event: Any = None) -> str:
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

        return self.correct_for_sushiswap(event, exchange_name_default)

    def get_pool_contract(self, exchange_name: str, address: str) -> Contract:
        """
        Get the pool contract.

        Parameters
        ----------
        exchange_name : str
            The exchange name.
        address : str
            The address.

        Returns
        -------
        Contract
            The pool contract.

        """
        default_contract = self.web3.eth.contract(
            address=address, abi=self.exchanges[exchange_name].get_abi()
        )
        contract_key = self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS if exchange_name == "bancor_v3" else address
        return self.pool_contracts[exchange_name].get(contract_key, default_contract)

    def add_pool_info(
            self,
            address: str,
            exchange_name: str,
            fee: Any,
            fee_float: float,
            tkn0_address: str,
            tkn1_address: str,
            cid: Optional[str] = None,
            other_args: Optional[Dict[str, Any]] = None,
            contract: Optional[Contract] = None,
    ) -> Dict[str, Any]:
        """
        This is the main function for adding pool info.
        Parameters
        ----------
        address : str
            The address.
        exchange_name : str
            The exchange name.
        fee : Any
            The fee.
        fee_float : float
            The fee float.
        tkn0_address : str
            The token 0 address.
        tkn1_address : str
            The token 1 address.
        cid : Optional[str], optional
            The cid.
        other_args : Optional[Dict[str, Any]], optional
            The other args.
        contract : Optional[Contract], optional
            The contract.

        Returns
        -------
        Dict[str, Any]
            The pool info.


        """
        # Get or Create ERC20 contracts for each token
        t0_symbol, t0_decimals = self.get_tkn_info(tkn0_address)
        if not t0_symbol:
            return None
        t1_symbol, t1_decimals = self.get_tkn_info(tkn1_address)
        if not t1_symbol:
            return None

        # Generate pool info
        pool_info = self.generate_pool_info(
            address, exchange_name, tkn0_address, tkn1_address, t0_symbol, t1_symbol,
            t0_decimals, t1_decimals, cid, fee, fee_float)

        # Add other args if necessary
        if other_args:
            pool_info.update(other_args)

        # Update cid if necessary
        if exchange_name != "carbon_v1":
            pool_info["cid"] = self.pool_cid_from_descr(self.web3, pool_info["descr"])

        # Add pool to exchange if necessary
        pool = self.get_or_init_pool(pool_info)
        assert pool, f"Pool not found in {exchange_name} pools"

        if contract:
            pool_info.update(pool.update_from_contract(contract))

        self.pool_data.append(pool_info)
        return pool_info

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
            self.web3, self.erc20_contracts, self.cfg, self.web3.toChecksumAddress(address)
        )
        return tkns or (None, None)

    def generate_pool_info(
            self, address, exchange_name, tkn0_address, tkn1_address,
            t0_symbol, t1_symbol, t0_decimals, t1_decimals, cid, fee, fee_float
    ) -> Dict[str, Any]:
        """
        Generate the pool info.

        Parameters
        ----------
        address : str
            The address.
        exchange_name : str
            The exchange name.
        tkn0_address : str
            The token 0 address.
        tkn1_address : str
            The token 1 address.
        t0_symbol : str
            The token 0 symbol.
        t1_symbol : str
            The token 1 symbol.
        t0_decimals : int
            The token 0 decimals.
        t1_decimals : int
            The token 1 decimals.
        cid : str
            The cid.
        fee : Any
            The fee.
        fee_float : float
            The fee float.

        Returns
        -------
        Dict[str, Any]
            The pool info.

        """
        pool_info = {
            "last_updated_block": self.web3.eth.blockNumber,
            "address": address,
            "exchange_name": exchange_name,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
            "tkn0_symbol": t0_symbol,
            "tkn1_symbol": t1_symbol,
            "tkn0_decimals": t0_decimals,
            "tkn1_decimals": t1_decimals,
            "cid": cid,
            "tkn0_key": f"{t0_symbol}-{tkn0_address[-4:]}",
            "tkn1_key": f"{t1_symbol}-{tkn1_address[-4:]}",
            "pair_name": f"{t0_symbol}-{tkn0_address[-4:]}/{t1_symbol}-{tkn1_address[-4:]}",
            "fee_float": fee_float,
            "fee": fee,
        }
        pool_info["descr"] = self.pool_descr_from_info(pool_info)
        return pool_info


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
            with brownie.multicall(address=self.cfg.MULTICALL_CONTRACT_ADDRESS):

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
                all_pairs = [
                    (pair[0], pair[1], 0, 5000) for pair in pairs + pairs_reverse
                ]

                # Fetch strategies for each pair from the CarbonController contract object
                strategies_by_pair = [
                    carbon_controller.strategiesByPair(*pair) for pair in all_pairs
                ]

                # Log the time taken for the above operations
                self.cfg.logger.info(f"Fetched {len(strategies_by_pair)} carbon strategies in {time.time() - start_time} seconds")

            start_time = time.time()

            # expand strategies_by_pair
            strategies_by_pair = [
                s for strat in strategies_by_pair if strat for s in strat if s
            ]

            # Create pool info for each strategy
            for strategy in strategies_by_pair:
                if len(strategy) > 0:
                    self.add_pool_info_from_strategy(strategy)

            # Log the time taken for the above operations
            self.cfg.logger.info(f"Updated {len(strategies_by_pair)} carbon strategies info in {time.time() - start_time} seconds")

        return [
            i
            for i, pool_info in enumerate(self.pool_data)
            if pool_info["last_updated_block"]
               < update_from_contract_block - self.alchemy_max_block_fetch
        ]

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

    def get_token_info_from_config(self, cfg: Config, addr: str) -> Optional[Tuple[str, int]]:
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
        for address_attr, info in self.TOKENS_MAPPING.items():
            if addr in [getattr(cfg, address_attr)]:
                return info
        return None

    def get_token_info_from_contract(self, web3: Web3, erc20_contracts: Dict[str, Contract], addr: str) -> Tuple[str, int]:
        """
        Get the token info from contract.

        Parameters
        ----------
        web3 : Web3
            The web3 instance.
        erc20_contracts : Dict[str, Contract]
            The erc20 contracts.
        addr : str
            The address.

        Returns
        -------
        Tuple[str, int]
            The token info.

        """
        contract = self.get_or_create_token_contracts(web3, erc20_contracts, addr)
        try:
            return contract.functions.symbol().call(), contract.functions.decimals().call()
        except Exception as e:
            self.cfg.logger.debug(f"Failed to get symbol and decimals for {addr} {e}")

    def add_pool_to_exchange(self, pool_info: Dict[str, Any]):
        """
        Add a pool to the exchange.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        """
        pool_type = self.pool_type_from_exchange_name(pool_info["exchange_name"])
        pool = pool_type(state=pool_info)
        self.exchanges[pool_info["exchange_name"]].add_pool(pool)

    def validate_pool_info(
            self,
            addr: Optional[str] = None,
            event: Optional[Dict[str, Any]] = None,
            pool_info: Optional[Dict[str, Any]] = None,
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

        Returns
        -------
        Optional[Dict[str, Any]]
            The pool info.

        """
        if pool_info is None or not pool_info:
            pool_info = self.add_pool_info_from_contract(address=addr, event=event)

        if addr == self.cfg.CARBON_CONTROLLER_ADDRESS:
            cid = event["args"]["id"]
            for pool in self.pool_data:
                if pool["cid"] == cid:
                    pool_info = pool
                    break

        if isinstance(pool_info, float):
            return

        return pool_info

    def update_from_event(self, event: Dict[str, Any]) -> None:
        """
        Updates the state of the pool data from an event.

        Parameters
        ----------
        event  : Dict[str, Any]
            The event.

        """
        addr = self.web3.toChecksumAddress(event["address"])
        ex_name = self.exchange_name_from_event(event)

        ex_name = self.correct_for_sushiswap(event, ex_name)
        if not ex_name:
            return

        key, key_value = self.get_key_and_value(event, addr, ex_name)
        pool_info = self.get_pool_info(key, key_value, ex_name) or self.add_pool_info_from_contract(address=addr, event=event, exchange_name=ex_name)

        if not pool_info:
            return

        pool = self.get_or_init_pool(pool_info)
        data = pool.update_from_event(event or {}, pool.get_common_data(event, pool_info) or {})

        if event['event'] == 'StrategyDeleted':
            self.handle_strategy_deleted(event)
            return

        self.update_pool_data(pool_info, data)

    def correct_for_sushiswap(self, event, ex_name):
        if ex_name and ex_name == 'uniswap_v2':
            ex_name = self.uniswap_v2_event_mappings.get(event['address'])
        return ex_name

    def get_key_and_value(self, event: Dict[str, Any], addr: str, ex_name: str) -> Tuple[str, Any]:
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
            value = event["args"]["tkn_address"] if event["args"]["tkn_address"] != self.cfg.BNT_ADDRESS else event["args"]["pool"]
            return "tkn1_address", value

    def get_pool_info(self, key: str, key_value: str, ex_name: str, event: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get the pool info.

        Parameters
        ----------
        key : str
            The key.
        key_value : str
            The key value.
        ex_name : str
            The exchange name.
        event : Optional[Dict[str, Any]], optional
            The event, by default None.

        Returns
        -------
        Optional[Dict[str, Any]]
            The pool info.
        """
        if ex_name == "sushiswap_v2":
            ex_name = "uniswap_v2"

        return next(
            (
                self.validate_pool_info(
                    self.web3.toChecksumAddress(key_value), event, pool
                )
                for pool in self.pool_data
                if pool[key] == key_value and pool["exchange_name"] == ex_name
            ),
            None,
        )

    def handle_strategy_deleted(self, event: Dict[str, Any]) -> None:
        """
        Handle the strategy deleted event.

        Parameters
        ----------
        event : Dict[str, Any]
            The event.
        """
        cid = event['args']['id']
        self.pool_data = [p for p in self.pool_data if p['cid'] != cid]
        self.exchanges['carbon_v1'].delete_strategy(event['args']['id'])

    def update_pool_data(self, pool_info: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Update the pool data.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.
        data : Dict[str, Any]
            The data.
        """
        for pool in self.pool_data:
            if pool["cid"] == pool_info["cid"]:
                pool.update(data)
                break


    def deduplicate_pool_data(self) -> None:
        """
        Deduplicate the pool data.
        """
        self.pool_data = sorted(self.pool_data, key=lambda x: x['last_updated_block'], reverse=True)
        seen = set()
        no_duplicates = [d for d in self.pool_data if d['cid'] not in seen and not seen.add(d['cid'])]
        self.pool_data = no_duplicates

    def update_from_pool_info(
            self, pool_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update the pool info.

        Parameters
        ----------
        pool_info : Optional[Dict[str, Any]], optional
            The pool info, by default None.
        """
        pool_info["last_updated_block"] = self.web3.eth.blockNumber
        contract = self.pool_contracts[pool_info["exchange_name"]].get(
            pool_info["address"],
            self.web3.eth.contract(
                address=pool_info["address"],
                abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
            ),
        ) if pool_info['exchange_name'] != 'bancor_v3' else self.pool_contracts[pool_info["exchange_name"]].get(self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS)
        pool = self.get_or_init_pool(pool_info)
        params = pool.update_from_contract(contract)
        for key, value in params.items():
            pool_info[key] = value
        return pool_info

    def update_from_contract(
            self, address: str = None, contract: Optional[Contract] = None, pool_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update the state from the contract (instead of events).

        Parameters
        ----------
        address : str, optional
            The address, by default None.
        contract : Optional[Contract], optional
            The contract, by default None.
        pool_info : Optional[Dict[str, Any]], optional
            The pool info, by default None.

        Returns
        -------
        Dict[str, Any]
            The pool info.
        """
        if pool_info:
            address = pool_info["address"]

        addr = self.web3.toChecksumAddress(address)

        if not pool_info:
            for pool in self.pool_data:
                if pool["address"] == addr:
                    pool_info = pool
                    break

        pool_info = self.validate_pool_info(addr=addr, pool_info=pool_info)
        if not pool_info:
            return

        pool_info["last_updated_block"] = self.web3.eth.blockNumber
        if contract is None:
            contract = self.pool_contracts[pool_info["exchange_name"]].get(
                pool_info["address"],
                self.web3.eth.contract(
                    address=pool_info["address"],
                    abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
                ),
            )
        pool = self.get_or_init_pool(pool_info)
        params = pool.update_from_contract(contract)
        for key, value in params.items():
            pool_info[key] = value
        return pool_info

    def get_or_init_pool(self, pool_info: Dict[str, Any]) -> Pool:
        """
        Get or init the pool.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        Returns
        -------
        Pool
            The pool.
        """
        key = self.pool_key_from_info(pool_info)
        pool = self.exchanges[pool_info["exchange_name"]].get_pool(key)
        if not pool:
            self.add_pool_to_exchange(pool_info)
            key = self.pool_key_from_info(pool_info)
            pool = self.exchanges[pool_info["exchange_name"]].get_pool(key)
        return pool

    @staticmethod
    def pool_key_from_info(pool_info: Dict[str, Any]) -> str:
        """
        Get the pool key from the pool info.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        Returns
        -------
        str
            The pool key.

        """
        if pool_info["exchange_name"] in ["uniswap_v2", "sushiswap_v2", "uniswap_v3"]:
            return pool_info["address"]
        elif pool_info["exchange_name"] == "carbon_v1":
            return pool_info["cid"]
        elif pool_info["exchange_name"] == "bancor_v3":
            return pool_info["tkn1_address"]

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

    def update(
            self,
            event: Dict[str, Any] = None,
            address: str = None,
            pool_info: Dict[str, Any] = None,
            contract: Contract = None,
    ) -> None:
        """
        Update the state.

        Parameters
        ----------
        event : Dict[str, Any], optional
            The event, by default None.
        address : str, optional
            The address, by default None.
        pool_info : Dict[str, Any], optional
            The pool info, by default None.
        contract : Contract, optional
            The contract, by default None.


        Raises
        ------
        Exception
            If the alchemy rate limit is hit.
            If no event or pool info is provided.
            If the pool info is invalid.
        """
        while True:
            rate_limiter = 0.1 + 0.9 * random.random()

            try:
                time.sleep(rate_limiter)
                if event:
                    self.update_from_event(event)
                elif address:
                    self.update_from_contract(address, contract)
                elif pool_info:
                    self.update_from_pool_info(pool_info)
                else:
                    self.cfg.logger.debug(
                        f"No event or pool info provided {event} {address} {contract}"
                    )
                    break
                break
            except Exception as e:
                if any(err_msg in str(e) for err_msg in ["Too many requests"]):
                    self.cfg.logger.debug(
                        f"Alchemy rate limit hit. Retrying after a {rate_limiter} second delay... {e}  {event} {address} {contract}"
                    )
                    time.sleep(rate_limiter)
                else:
                    self.cfg.logger.error(f"Error updating pool: {e} {event} {address} {contract}")
                    break
