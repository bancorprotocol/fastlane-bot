"""
Contains the manager module for handling contract functionality within the events updater.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""

import os.path
import random
from datetime import datetime
from glob import glob
from typing import Dict, Any, Tuple, List

import pandas as pd
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.data.abi import (
    BANCOR_V3_NETWORK_INFO_ABI,
    ERC20_ABI,
    BANCOR_POL_ABI,
    BALANCER_VAULT_ABI,
)
from fastlane_bot.events.managers.base import BaseManager
from fastlane_bot.events.pools.utils import get_pool_cid
from ..interfaces.event import Event


class ContractsManager(BaseManager):
    def init_tenderly_event_contracts(self):
        """
        Initialize the tenderly event contracts.
        """

        for exchange_name in self.tenderly_event_exchanges:

            if exchange_name == "bancor_pol":
                self.tenderly_event_contracts[
                    exchange_name
                ] = self.w3_tenderly.eth.contract(
                    address=self.cfg.BANCOR_POL_ADDRESS,
                    abi=self.exchanges[exchange_name].get_abi(),
                )
            elif exchange_name == "bancor_v3":
                self.tenderly_event_contracts[
                    exchange_name
                ] = self.w3_tenderly.eth.contract(
                    address=self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS,
                    abi=BANCOR_V3_NETWORK_INFO_ABI,
                )
            elif exchange_name in self.cfg.CARBON_V1_FORKS:
                self.tenderly_event_contracts[
                    exchange_name
                ] = self.w3_tenderly.eth.contract(
                    address=self.cfg.CARBON_CONTROLLER_MAPPING[exchange_name],
                    abi=self.exchanges[exchange_name].get_abi(),
                )
            elif exchange_name == "pancakeswap_v2":
                self.tenderly_event_contracts[
                    exchange_name
                ] = self.w3_tenderly.eth.contract(
                    address=self.cfg.PANCAKESWAP_V2_FACTORY_ADDRESS,
                    abi=self.exchanges[exchange_name].get_abi(),
                )
            elif exchange_name == "pancakeswap_v3":
                self.tenderly_event_contracts[
                    exchange_name
                ] = self.w3_tenderly.eth.contract(
                    address=self.cfg.PANCAKESWAP_V3_FACTORY_ADDRESS,
                    abi=self.exchanges[exchange_name].get_abi(),
                )
            else:
                raise NotImplementedError(
                    f"Exchange {exchange_name} not supported for tenderly"
                )

    def init_exchange_contracts(self):
        """
        Initialize the exchange contracts.
        """
        for fork in self.cfg.UNI_V2_FORKS:
            self.pool_contracts[fork] = {}
        for fork in self.cfg.UNI_V3_FORKS:
            self.pool_contracts[fork] = {}
        for fork in self.cfg.CARBON_V1_FORKS:
            self.pool_contracts[fork] = {}
            self.carbon_inititalized[fork] = False
        for fork in self.cfg.SOLIDLY_V2_FORKS:
            self.pool_contracts[fork] = {}

        for exchange_name in self.SUPPORTED_EXCHANGES:
            self.pool_contracts[exchange_name] = {}

            if exchange_name == "bancor_v3":
                self.pool_contracts[exchange_name][
                    self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS
                ] = self.web3.eth.contract(
                    address=self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS,
                    abi=BANCOR_V3_NETWORK_INFO_ABI,
                )
            elif exchange_name == "bancor_pol":
                self.pool_contracts[exchange_name][
                    self.cfg.BANCOR_POL_ADDRESS
                ] = self.web3.eth.contract(
                    address=self.cfg.BANCOR_POL_ADDRESS,
                    abi=BANCOR_POL_ABI,
                )
            elif exchange_name == "balancer":
                self.pool_contracts[exchange_name][
                    self.cfg.BALANCER_VAULT_ADDRESS
                ] = self.web3.eth.contract(
                    address=self.cfg.BALANCER_VAULT_ADDRESS,
                    abi=BALANCER_VAULT_ABI,
                )


    @staticmethod
    def get_or_create_token_contracts(
        web3: Web3,
        erc20_contracts: Dict[str, Contract],
        address: str,
        exchange_name: str = None,
        tenderly_fork_id: str = None,
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
        exchange_name : str, optional
            The exchange name.
        tenderly_fork_id : str, optional
            The tenderly fork id.

        Returns
        -------
        Contract
            The token contract.

        """
        if exchange_name == "bancor_pol" and tenderly_fork_id:
            w3 = Web3(
                Web3.HTTPProvider(f"https://rpc.tenderly.co/fork/{tenderly_fork_id}")
            )
            contract = w3.eth.contract(abi=ERC20_ABI, address=address)
        elif address in erc20_contracts:
            contract = erc20_contracts[address]
        else:
            contract = web3.eth.contract(address=address, abi=ERC20_ABI)
            erc20_contracts[address] = contract
        return contract

    def add_pool_info_from_contract(
        self,
        exchange_name: str = None,
        address: str = None,
        event: Event = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
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
            self.cfg.logger.warning(
                f"[events.managers.contracts] Exchange name not found {event}. Skipping event..."
            )
            return None

        if exchange_name not in self.SUPPORTED_EXCHANGES:
            self.cfg.logger.warning(
                f"Event exchange {exchange_name} not in exchanges={self.SUPPORTED_EXCHANGES} for address={address}. "
                f"Skipping event..."
            )
            return None

        pool_contract = self.get_pool_contract(exchange_name, address)
        self.pool_contracts[exchange_name][address] = pool_contract
        fee, fee_float = self.exchanges[exchange_name].get_fee(address, pool_contract)

        t0_addr = self.exchanges[exchange_name].get_tkn0(address, pool_contract, event)
        t1_addr = self.exchanges[exchange_name].get_tkn1(address, pool_contract, event)
        block_number = event.block_number
        strategy_id = event.args["id"] if exchange_name in self.cfg.CARBON_V1_FORKS else None
        temp_pool_info = {
            "exchange_name": exchange_name,
            "fee": f"{fee}",
            "pair_name": f"{t0_addr}/{t1_addr}",
            "strategy_id": strategy_id,
        }
        cid = get_pool_cid(temp_pool_info, self.cfg.CARBON_V1_FORKS)

        return self.add_pool_info(
            address=address,
            exchange_name=exchange_name,
            fee=fee,
            fee_float=fee_float,
            tkn0_address=t0_addr,
            tkn1_address=t1_addr,
            cid=cid,
            strategy_id=strategy_id,
            contract=pool_contract,
            block_number=block_number,
            tenderly_exchanges=tenderly_exchanges,
        )

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
        if exchange_name not in self.exchanges:
            return None

        w3 = self.web3

        contract_key = (
            self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS
            if exchange_name == "bancor_v3"
            else self.cfg.BANCOR_POL_ADDRESS
            if exchange_name == "bancor_pol"
            else address
        )
        return self.pool_contracts[exchange_name].get(
            contract_key,
            w3.eth.contract(
                address=contract_key, abi=self.exchanges[exchange_name].get_abi()
            ),
        )


    def get_token_info_from_contract(
        self, web3: Web3, erc20_contracts: Dict[str, Contract], addr: str
    ) -> Tuple[str, int]:
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
        tokens_filepath = os.path.normpath(
            f"fastlane_bot/data/blockchain_data/{self.cfg.NETWORK}/tokens.csv"
        )
        token_data = pd.read_csv(tokens_filepath)
        extra_info = glob(
            os.path.normpath(
                f"{self.prefix_path}fastlane_bot/data/blockchain_data/{self.cfg.NETWORK}/token_detail/*.csv"
            )
        )
        if len(extra_info) > 0:
            extra_info_df = pd.concat(
                [pd.read_csv(f) for f in extra_info], ignore_index=True
            )
            token_data = pd.concat([token_data, extra_info_df], ignore_index=True)
            token_data = token_data.drop_duplicates(subset=["address"])
            self.tokens = token_data.to_dict(orient="records")
        try:
            return self._get_and_save_token_info_from_contract(
                contract=contract,
                addr=addr,
                token_data=token_data,
                tokens_filepath=tokens_filepath
            )
        except self.FailedToGetTokenDetailsException as e:
            self.cfg.logger.debug(
                f"[events.managers.contracts.get_token_info_from_contract] {e}"
            )

    class FailedToGetTokenDetailsException(Exception):
        """
        Exception caused when token details are unable to be fetched by the contract
        """

        def __init__(self, addr):
            self.message = f"[events.managers.contracts.get_token_info_from_contract] Failed to get token symbol and decimals for token address: {addr}"

        def __str__(self):
            return self.message

    def _get_and_save_token_info_from_contract(
        self,
        contract: Contract,
        addr: str,
        token_data: pd.DataFrame,
        tokens_filepath: str,
    ) -> Tuple[str, int]:
        """
        Get and save the token info from contract to csv.

        Parameters
        ----------
        contract : Contract
            The contract.
        addr : str
            The address.
        token_data : pd.DataFrame
            The token data.
        tokens_filepath : str
            The tokens filepath.

        Returns
        -------
        Tuple[str, int]
            The token info.

        """
        try:
            symbol = contract.functions.symbol().call()
        except OverflowError:
            raise self.FailedToGetTokenDetailsException(addr=addr)

        if addr in token_data["address"].unique():
            decimals = token_data.loc[token_data["address"] == addr, "decimals"].iloc[0]
            return symbol, decimals
        else:
            decimals = int(float(contract.functions.decimals().call()))

        if (
            symbol is None
            or decimals is None
            or type(symbol) != str
            or type(decimals) != int
        ):
            raise self.FailedToGetTokenDetailsException(addr=addr)
        symbol = str(symbol).replace("-", "_")
        new_data = {
            "symbol": symbol,
            "address": addr,
            "decimals": decimals,
        }
        try:

            self.cfg.logger.debug(
                f"[events.managers.contracts._get_and_save_token_info_from_contract] Adding new token {symbol} to {tokens_filepath}"
            )
        except UnicodeEncodeError:
            raise self.FailedToGetTokenDetailsException(addr=addr)

        row = pd.DataFrame(new_data, columns=token_data.columns, index=[1])
        if not os.path.exists(
            os.path.normpath(
                f"{self.prefix_path}fastlane_bot/data/blockchain_data/{self.cfg.NETWORK}/token_detail"
            )
        ):
            try:
                os.mkdir(
                    os.path.normpath(
                        f"{self.prefix_path}fastlane_bot/data/blockchain_data/{self.cfg.NETWORK}/token_detail"
                    )
                )
            except FileExistsError:
                pass

        if not self.read_only:
            collision_safety = str(random.randrange(1, 1000))
            ts = datetime.now().strftime("%d-%H-%M-%S-%f")
            ts += collision_safety
            row.to_csv(
                os.path.normpath(
                    f"{self.prefix_path}fastlane_bot/data/blockchain_data/{self.cfg.NETWORK}/token_detail/{ts}.csv"
                ),
                index=False,
            )

        return (symbol, decimals)
