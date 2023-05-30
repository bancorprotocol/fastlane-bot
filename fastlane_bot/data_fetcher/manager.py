import random
import time
from dataclasses import field, dataclass
from typing import Dict, Any, List, Type, Hashable, Optional, Callable, Tuple

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
    This class represents a Manager which manages various components and configurations
    needed to run the operations.

    Attributes:
        web3 (Web3): Instance of Web3, which allows for interaction with the Ethereum blockchain.
        cfg (Config): Config object that holds configuration details.
        pool_data (List[Dict[str, Any]]): List of dictionaries, each containing data related to a liquidity pool.
        alchemy_max_block_fetch (int): Maximum number of blocks to fetch from alchemy.
        event_contracts (Dict[str, Contract or Type[Contract]]): Mapping of event names to their respective Contract instances.
        pool_contracts (Dict[str, Contract or Type[Contract]]): Mapping of pool addresses to their respective Contract instances.
        erc20_contracts (Dict[str, Contract or Type[Contract]]): Mapping of ERC20 token addresses to their respective Contract instances.
        exchanges (Dict[str, Exchange]): Mapping of exchange names to their respective Exchange instances.
        SUPPORTED_EXCHANGES (List[str]): List of supported exchange names.
    """

    web3: Web3
    cfg: Config
    pool_data: List[Dict[str, Any]]
    alchemy_max_block_fetch: int
    event_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    pool_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    erc20_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)
    exchanges: Dict[str, Exchange] = field(default_factory=dict)
    SUPPORTED_EXCHANGES: List[str] = None

    def __post_init__(self):
        for exchange_name in self.SUPPORTED_EXCHANGES:
            self.exchanges[exchange_name] = exchange_factory.get_exchange(exchange_name)
        self.init_exchange_contracts()

    def init_exchange_contracts(self):
        """
        This method initializes the contracts for the supported exchanges. For each supported exchange, it sets up
        an event contract and an empty dictionary for the pool contracts.

        The event contract for an exchange is an Ethereum contract instance created using the ABI (Application Binary Interface)
        provided by the corresponding exchange instance. The ABI is a JSON representation of the contract, including all of its methods
        and the correct way to call them.

        The pool contract for an exchange is initially an empty dictionary. This dictionary will later be filled with Ethereum contract
        instances representing specific pools on the exchange.

        Note: This method assumes that for each supported exchange, there exists an Exchange instance with the same name in `self.exchanges`.
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
        A static method that returns an ERC20 token contract for a given address. If the contract already exists in
        the dictionary of erc20_contracts, it is simply returned. Otherwise, a new contract is created using the
        provided web3 instance and ERC20_ABI, then added to the dictionary.

        Args:
            web3 (Web3): The instance of Web3 to be used for contract creation.
            erc20_contracts (Dict[str, Contract]): The dictionary where the existing contracts are stored. The keys are
            the contract addresses and the values are the corresponding Contract objects.
            address (str): The address of the ERC20 token contract to be returned.

        Returns:
            Contract: The ERC20 token contract corresponding to the given address.

        Raises:
            AssertionError: If the address is not valid.
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
        A static method that determines the name of the exchange corresponding to the given event based on the event's
        format. It iterates over the pool_factory's creators (a dictionary of exchange names and their corresponding
        pool classes) and checks if the pool_class's event format matches the format of the event.

        Args:
            event (Dict[str, Any]): The event whose corresponding exchange's name is to be returned. It should be a
            dictionary that contains 'args' key, representing event arguments.

        Returns:
            str: The name of the exchange corresponding to the given event. If no matching exchange is found, None is
            returned.
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
        A static method that gets the pool type corresponding to the given exchange name using a pool factory. The pool
        type is returned as a callable object.

        Args:
            exchange_name (str): The name of the exchange for which the pool type is required.

        Returns:
            Callable: A callable object representing the pool type corresponding to the given exchange name.
        """
        return pool_factory.get_pool(exchange_name)

    @staticmethod
    def pool_descr_from_info(pool_info: Dict[str, Any]) -> str:
        """
        A static method that generates a descriptive string for a pool based on its information.

        Args:
            pool_info (Dict[str, Any]): A dictionary containing information about the pool. It should contain keys for
            'exchange_name', 'pair_name', and 'fee'.

        Returns:
            str: A descriptive string for the pool, constructed by joining the pool's exchange name, pair name, and fee.
        """
        return (
            f"{pool_info['exchange_name']} {pool_info['pair_name']} {pool_info['fee']}"
        )

    @staticmethod
    def pool_cid_from_descr(web3: Web3, descr: str) -> str:
        """
        A static method that generates a unique identifier (cid) for a pool based on its description.

        Args:
            web3 (Web3): An instance of a web3.py Web3 class which provides access to the Ethereum blockchain and its APIs.
            descr (str): The description string of the pool.

        Returns:
            str: A hexadecimal string representing the unique identifier (cid) of the pool, derived by hashing the description string.
        """
        return web3.keccak(text=descr).hex()

    @property
    def events(self) -> List[Type[Contract]]:
        """
        This property represents a list of all events from all exchanges managed by this Manager instance.

        Returns:
            List[Type[Contract]]: A list of contract types which represent the events of all exchanges managed by this instance.
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
        This property represents a list of all pools from all exchanges managed by this Manager instance.

        Returns:
            List[Pool]: A list of pools from all exchanges managed by this instance.
        """
        return [
            pool
            for exchange in self.exchanges.values()
            for pool in exchange.get_pools()
        ]

    def add_pool_info_from_strategy(self, strategy: List[Any]) -> Dict[str, Any]:
        """
        Add pool information based on the provided strategy.

        Args:
            strategy (List[Any]): The strategy containing the pool information.

        Returns:
            Dict[str, Any]: The added pool information.

        Raises:
            ValueError: If the provided strategy is not in the expected format.
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

    def add_pool_info_from_contract(
        self, exchange_name: str = None, address: str = None, event: Any = None
    ) -> Dict[str, Any]:
        """
        Add pool information based on the provided contract.

        Args:
            exchange_name (str): The name of the exchange associated with the contract.
            address (str): The address of the contract.
            event (Any): The event associated with the contract.

        Returns:
            Dict[str, Any]: The added pool information.

        Notes:
            If `exchange_name` is not provided, it will be determined based on the event. The method fetches the
            pool contract associated with the provided exchange name and address. If the contract is not already stored
            in the `pool_contracts` dictionary, it will be retrieved from the Ethereum network using the provided address
            and the exchange's ABI. The retrieved contract is then stored in the `pool_contracts` dictionary for future
            use. The fee and fee_float values are obtained using the exchange's `get_fee` method with the address and
            pool contract. The token addresses are fetched from the pool contract using the exchange's `get_tkn0` and
            `get_tkn1` methods with the address, pool contract, and event. The pool information is added using the
            `add_pool_info` method with the necessary parameters obtained from the contract and event. The added pool
            information is returned as a dictionary.

        """
        if exchange_name is None:
            exchange_name = self.exchange_name_from_event(event)

        # Get pool contract
        pool_contract = self.pool_contracts[exchange_name].get(
            address,
            self.web3.eth.contract(
                address=address, abi=self.exchanges[exchange_name].get_abi()
            ),
        ) if exchange_name != "bancor_v3" else self.pool_contracts[exchange_name].get(
            self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS)
        self.pool_contracts[exchange_name][address] = pool_contract
        fee, fee_float = self.exchanges[exchange_name].get_fee(address, pool_contract)

        # Fetch token addresses from pool contract
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
    ):
        """
        Add pool information based on the provided parameters.

        Args:
            address (str): The address of the pool.
            exchange_name (str): The name of the exchange associated with the pool.
            fee (Any): The fee associated with the pool.
            fee_float (float): The floating-point representation of the fee.
            tkn0_address (str): The address of the first token.
            tkn1_address (str): The address of the second token.
            cid (Optional[str]): The CID (Carbon ID) of the pool.
            other_args (Optional[Dict[str, Any]]): Additional arguments for the pool information.
            contract (Optional[Contract]): The contract associated with the pool.

        Returns:
            Dict[str, Any]: The added pool information.

        Notes:
            The method generates pool information based on the provided parameters. It retrieves or creates ERC20
            contracts for each token using the provided web3 instance, erc20_contracts dictionary, and configuration. The
            pool information includes details such as the last updated block, pool address, exchange name,
            token addresses, token symbols, token decimals, CID, token keys, pair name, fee, and fee_float. The
            description (descr) of the pool is generated using the `pool_descr_from_info` method. If `other_args` is
            provided, the additional arguments are added to the pool information using the `update` method. If the
            exchange name is not "carbon_v1", the CID is updated by generating it from the pool description using the
            `pool_cid_from_descr` method. If a contract is provided, the pool information is updated from the contract
            using the `update_from_contract` method. The updated information is added to the pool information dictionary.
            The pool information is appended to the `pool_data` list and returned.


        """
        # Get or Create ERC20 contracts for each token
        t0_symbol, t0_decimals = self.get_tkn_symbol_and_decimals(
            self.web3, self.erc20_contracts, self.cfg, self.web3.toChecksumAddress(tkn0_address)
        )
        t1_symbol, t1_decimals = self.get_tkn_symbol_and_decimals(
            self.web3, self.erc20_contracts, self.cfg, self.web3.toChecksumAddress(tkn1_address)
        )

        # Generate pool info
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

        # Add other args if necessary
        if other_args is not None:
            pool_info.update(other_args)

        # Update cid if necessary
        if exchange_name != "carbon_v1":
            pool_info["cid"] = self.pool_cid_from_descr(self.web3, pool_info["descr"])

        # Add pool to exchange if necessary
        pool = self.get_or_init_pool(pool_info)
        assert pool is not None, f"Pool not found in {exchange_name} pools"

        if contract is not None:
            other_args = pool.update_from_contract(contract)
            pool_info.update(other_args)

        self.pool_data.append(pool_info)
        return pool_info

    def get_rows_to_update(self, update_from_contract_block: int) -> List[int]:
        """
        Get the rows in the pool_data list that need to be updated from contracts.

        Args:
            update_from_contract_block (int): The block number from which the contracts are updated.

        Returns:
            List[Hashable]: The indices of the rows in pool_data that need to be updated.

        Notes:
            The method retrieves the rows in the pool_data list that have a last_updated_block value earlier than
            `update_from_contract_block - self.alchemy_max_block_fetch`. This ensures that only the rows that have not
            been recently updated are included in the returned list. If the exchange "carbon_v1" is supported,
            the method performs additional operations specific to the CarbonController contract. It fetches strategies
            for each pair from the CarbonController contract, creates pool information for each strategy using the
            `add_pool_info_from_strategy` method, and logs the time taken for these operations. The resulting list of
            rows to update is returned as a list of indices.

        """

        if "carbon_v1" in self.SUPPORTED_EXCHANGES:
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

            # expand strategies_by_pair
            strategies_by_pair = [
                s for strat in strategies_by_pair if strat for s in strat if s
            ]

            # Create pool info for each strategy
            for strategy in strategies_by_pair:
                if len(strategy) > 0:
                    self.add_pool_info_from_strategy(strategy)

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
        Get the symbol and decimals of a token.

        Args:
            web3 (Web3): The Web3 instance.
            erc20_contracts (Dict[str, Contract]): A dictionary of ERC20 contracts.
            cfg (Config): The Config instance.
            addr (str): The address of the token.

        Returns:
            Tuple[str, int]: A tuple containing the symbol and decimals of the token.

        Notes:
            If the address is equal to `cfg.ETH_ADDRESS`, it returns the symbol "ETH" and decimals 18.

            Otherwise, it retrieves the token contract using the `get_or_create_token_contracts` method,
            and calls the `symbol` and `decimals` functions of the contract to get the symbol and decimals
            of the token, respectively.

        """
        if addr in [cfg.ETH_ADDRESS]:
            return "ETH", 18
        if addr in [cfg.WETH_ADDRESS]:
            return "WETH", 18
        if addr in [cfg.WBTC_ADDRESS]:
            return "WBTC", 8
        if addr in [cfg.BNT_ADDRESS]:
            return "BNT", 18
        if addr in [cfg.USDC_ADDRESS]:
            return "USDC", 6
        contract = self.get_or_create_token_contracts(web3, erc20_contracts, addr)
        try:
            return contract.functions.symbol().call(), contract.functions.decimals().call()
        except Exception as e:
            print(f"Failed to get symbol and decimals for {addr} {e}")

    def add_pool_to_exchange(self, pool_info: Dict[str, Any]) -> None:
        """
        Add a pool to the corresponding exchange.

        Args:
            pool_info (Dict[str, Any]): The pool information.

        Notes:
            The method retrieves the pool type based on the exchange name using the
            `pool_type_from_exchange_name` method. It creates a new pool instance
            using the pool type and the provided pool information. Finally, it adds
            the pool to the corresponding exchange.
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
        Validate the pool information.

        Args:
            addr (str, optional): The pool address.
            event (Dict[str, Any], optional): The event containing pool information.
            pool_info (Dict[str, Any], optional): The pool information.

        Returns:
            Optional[Dict[str, Any]]: The validated pool information or None.

        Notes:
            The method validates the provided pool information. If the `pool_info`
            argument is not provided or empty, it calls the `add_pool_info_from_contract`
            method to retrieve the pool information based on the address or event. If
            the address is the carbon controller address, it searches for a pool with
            a matching CID in the existing pool data. Finally, it returns the validated
            pool information.

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
        Update the Manager state based on an event.

        Args:
            event (Dict[str, Any]): The event data.

        Notes:
            The method updates the Manager state based on the provided event data.
            It extracts the address and exchange name from the event, and based on
            the exchange name, determines the key and key value to search for the
            corresponding pool information in the existing pool data. It then calls
            the `validate_pool_info` method to validate the pool information. If the
            pool information is valid, it retrieves or initializes the pool object and
            updates its information using the event and common data. Finally, it finds
            the corresponding pool in the list of pool data and updates its information.
        """
        addr = self.web3.toChecksumAddress(event["address"])
        ex_name = self.exchange_name_from_event(event)

        if ex_name == "carbon_v1":
            key = "cid"
            key_value = event["args"]["id"]
        elif ex_name in ["uniswap_v2", "sushiswap_v2", "uniswap_v3"]:
            key = "address"
            key_value = addr
        elif ex_name == "bancor_v3":
            print(f"bancor_v3 event: {event}")
            key = "tkn1_address"
            key_value = event["args"]["tkn_address"] if event["args"]["tkn_address"] != self.cfg.BNT_ADDRESS else event["args"]["pool"]

        pool_info = None
        for pool in self.pool_data:
            if pool[key] == key_value and pool["exchange_name"] == ex_name:
                pool_info = pool
                print(f"Found pool info: {pool_info}")
                break

        pool_info = self.validate_pool_info(addr, event, pool_info)
        if not pool_info:
            return

        pool = self.get_or_init_pool(pool_info)
        data = pool.update_from_event(
            event or {}, pool.get_common_data(event, pool_info) or {}
        )

        # Find the corresponding pool in the list and update its information
        for i, p in enumerate(self.pool_data):
            if p["cid"] == pool_info["cid"]:
                self.pool_data[i].update(data)
                break

    def update_from_pool_info(
            self, pool_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update the Manager state from a contract.

        Args:
            pool_info (Optional[Dict[str, Any]]): The pool information (optional).

        Returns:
            Dict[str, Any]: The updated pool information.

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
        Update the Manager state from a contract.

        Args:
            address (str): The address of the contract.
            contract (Optional[Contract]): The contract instance (optional).
            pool_info (Optional[Dict[str, Any]]): The pool information (optional).

        Returns:
            Dict[str, Any]: The updated pool information.

        Notes:
            The method updates the Manager state based on the provided contract address.
            It searches for the corresponding pool information in the existing pool data
            using the contract address. It then calls the `validate_pool_info` method to
            validate the pool information. If the pool information is valid, it updates
            the "last_updated_block" value to the current block number. If the contract
            instance is not provided, it retrieves the contract from the pool contracts
            dictionary based on the exchange name. It then retrieves or initializes the
            pool object and updates its information using the contract. Finally, it
            updates the pool information with the updated parameters and returns it.
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
        Get an existing pool or initialize a new pool.

        Args:
            pool_info (Dict[str, Any]): The pool information.

        Returns:
            Pool: The existing or initialized pool.

        Notes:
            The method checks if an existing pool with the given pool information
            exists in the Manager's exchanges. If a pool is found, it is returned.
            If no pool is found, the method adds the pool to the corresponding
            exchange using the `add_pool_to_exchange` method. It then retrieves
            the pool again and returns it.
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
        Generate a unique key for the pool based on the pool information.

        Args:
            pool_info (Dict[str, Any]): The pool information.

        Returns:
            str: The unique key for the pool.

        Notes:
            The method generates a unique key for the pool based on the exchange name
            in the pool information. For exchanges "uniswap_v2", "sushiswap_v2", and
            "uniswap_v3", the key is the pool address. For the "carbon_v1" exchange,
            the key is the CID. For the "bancor_v3" exchange, the key is the tkn1_address.
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
        Get the pool key value from the event based on the specified key.

        Args:
            key (str): The key to identify the pool property.
            event (Dict[str, Any]): The event data.

        Returns:
            Any: The pool key value.

        Notes:
            The method retrieves the corresponding pool key value from the event data
            based on the specified key. Supported keys are "cid", "address",
            "tkn0_address", and "tkn1_address", depending on the exchange name.
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
        Update the pool based on the provided event or contract.

        Args:
            event (Dict[str, Any], optional): The event data. Defaults to None.
            address (str, optional): The pool address. Defaults to None.
            pool_info (Dict[str, Any], optional): The pool information. Defaults to None.
            contract (Contract, optional): The pool contract. Defaults to None.

        Notes:
            The method updates the pool based on the provided event or contract.
            It first checks if an event or contract is provided. If an event is provided,
            it calls the `update_from_event` method to update the pool from the event.
            If an address and contract are provided, it calls the `update_from_contract`
            method to update the pool from the contract. If neither an event nor a contract
            is provided, it prints a message indicating that no event or pool info was provided.

        Raises:
            Exception: If the Alchemy rate limit is hit, the method retries after a random delay.
            Exception: If an error occurs while updating the pool, the method prints the error.

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
                    print(
                        f"No event or pool info provided {event} {address} {contract}"
                    )
                    break
                break
            except Exception as e:
                if any(err_msg in str(e) for err_msg in ["Too Many Requests for url"]):
                    print(
                        f"Alchemy rate limit hit. Retrying after a {rate_limiter} second delay... {e}  {event} {address} {contract}"
                    )
                    time.sleep(rate_limiter)
                else:
                    print(f"Error updating pool: {e} {event} {address} {contract}")
                    break
