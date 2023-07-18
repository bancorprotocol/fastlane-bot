# coding=utf-8
"""
Contains the manager module for handling contract functionality within the events updater.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Dict, Any, Tuple

import brownie
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.data.abi import BANCOR_V3_NETWORK_INFO_ABI, ERC20_ABI
from fastlane_bot.events.managers.base import BaseManager


class ContractsManager(BaseManager):
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
                self.pool_contracts[exchange_name][
                    self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS
                ] = brownie.Contract.from_abi(
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

    def add_pool_info_from_contract(
        self,
        exchange_name: str = None,
        address: str = None,
        event: Any = None,
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
            self.cfg.logger.info(f"Exchange name not found {event}")
            return None

        if exchange_name not in self.SUPPORTED_EXCHANGES:
            self.cfg.logger.debug(
                f"Event exchange {exchange_name} not in exchanges={self.SUPPORTED_EXCHANGES} for address={address}"
            )
            return None

        pool_contract = self.get_pool_contract(exchange_name, address)
        self.pool_contracts[exchange_name][address] = pool_contract
        fee, fee_float = self.exchanges[exchange_name].get_fee(address, pool_contract)

        t0_addr = self.exchanges[exchange_name].get_tkn0(address, pool_contract, event)
        t1_addr = self.exchanges[exchange_name].get_tkn1(address, pool_contract, event)
        block_number = event["blockNumber"]

        return self.add_pool_info(
            address=address,
            exchange_name=exchange_name,
            fee=fee,
            fee_float=fee_float,
            tkn0_address=t0_addr,
            tkn1_address=t1_addr,
            cid=event["args"]["id"] if exchange_name == "carbon_v1" else None,
            contract=pool_contract,
            block_number=block_number,
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
        if exchange_name in self.exchanges:
            default_contract = self.web3.eth.contract(
                address=address, abi=self.exchanges[exchange_name].get_abi()
            )
            contract_key = (
                self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS
                if exchange_name == "bancor_v3"
                else address
            )
            return self.pool_contracts[exchange_name].get(
                contract_key, default_contract
            )
        else:
            return None

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
        try:
            return (
                contract.functions.symbol().call(),
                contract.functions.decimals().call(),
            )
        except Exception as e:
            self.cfg.logger.debug(f"Failed to get symbol and decimals for {addr} {e}")
