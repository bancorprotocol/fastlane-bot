import time
from typing import Any

from web3 import Web3
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.helpers.txhelpers import TxHelpers

from fastlane_bot.data.abi import BANCOR_V3_NETWORK_ABI, BANCOR_V3_NETWORK_SETTINGS, BANCOR_V3_POOL_COLLECTION_ABI

class AutomaticPoolShutdown:
    """
    This is a standalone class to find Bancor V3 liquidity pools that are in surplus and automatically shut them down
    """
    mgr: Manager
    shutdown_whitelist: [] = None
    active_pools = {}
    poll_time: int = 12
    arb_mode = "pool_shutdown"

    def __init__(self, mgr: Manager):
        self.mgr = mgr
        self.__post_init__()

    def __post_init__(self):
        self.tx_helpers = TxHelpers(ConfigObj=self.mgr.cfg)
        self.bancor_network_contract = self.mgr.web3.eth.contract(address=self.mgr.web3.toChecksumAddress(self.mgr.cfg.BANCOR_V3_NETWORK_ADDRESS), abi=BANCOR_V3_NETWORK_ABI)
        self.bancor_settings_contract = self.mgr.web3.eth.contract(address=self.mgr.web3.toChecksumAddress(self.mgr.cfg.BANCOR_V3_NETWORK_SETTINGS), abi=BANCOR_V3_NETWORK_SETTINGS)
        self.pool_collection_contract = self.mgr.web3.eth.contract(address=self.mgr.web3.toChecksumAddress(self.mgr.cfg.BANCOR_V3_POOL_COLLECTOR_ADDRESS), abi=BANCOR_V3_POOL_COLLECTION_ABI)
        self.get_whitelist()

    def main_loop(self):
        """
        Run this function in a loop.
        """
        while True:
            self.main_sequence()

    def main_sequence(self):
        """
        This runs the main sequence of the mode:

        1: searches active pools to get their status and staked balance
        2: checks the balance of the Bancor V3 vault & compares it to the staked balance
        3: if a token is found in surplus, submits a TX to shut the pool down

        """
        self.mgr.cfg.logger.info(f"\n\nRunning AutomaticPoolShutdown main sequence.")
        self.parse_active_pools()
        self.mgr.cfg.logger.info(f"Pool data collected, checking vault token balances and comparing.")
        tkn_to_shutdown = self.iterate_active_pools()
        if tkn_to_shutdown is not None:
            self.mgr.cfg.logger.info(f"Found pool to shut down: {tkn_to_shutdown}, initiating launch sequence.")
            tx_hash = self.generate_shutdown_tx(tkn=tkn_to_shutdown)
        else:
            self.mgr.cfg.logger.info(f"No pools found to shut down. Waiting and restarting sequence.")
        time.sleep(self.poll_time)
    def get_whitelist(self):
        """
        This function gets the token whitelist from the Bancor V3 Network Settings contract.

        """
        self.shutdown_whitelist = self.bancor_settings_contract.caller.tokenWhitelistForPOL()

    def parse_active_pools(self):
        """
        This function uses a multicall to get pool details for each Bancor V3 token. If the pool is active, it updates the dict with the current staked balance. If the pool is inactive, it removes it from the dictionary if it existed previously.
        """
        with self.mgr.multicall(address=self.mgr.cfg.MULTICALL_CONTRACT_ADDRESS):
            for tkn in self.shutdown_whitelist:
                pool_token, trading_fee_PPM, trading_enabled, depositing_enabled, average_rate, tkn_pool_liquidity = self.pool_collection_contract.functions.poolData(tkn).call()
                tkn_results = [x for x in tkn_pool_liquidity]
                bnt_trading_liquidity, tkn_trading_liquidity, staked_balance = tkn_results
                self.active_pools[tkn] = staked_balance

    def iterate_active_pools(self):
        """
        This function iterates over each active pool and compares the balance of the Bancor V3 vault vs the staked balance. If the staked balance is greater, it will call the autoshutdown function.
        """
        for tkn in self.active_pools.keys():
            if tkn == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                eth_balance = self.mgr.web3.eth.get_balance(self.mgr.web3.toChecksumAddress(self.mgr.cfg.BANCOR_V3_VAULT))
                if eth_balance > 0 and eth_balance > self.active_pools[tkn]:
                    return tkn
            else:
                tkn_balance = self.get_vault_balance_of_tkn(tkn)
                if tkn_balance > 0 and tkn_balance > self.active_pools[tkn]:
                    return tkn
        return None



    def get_vault_balance_of_tkn(self, tkn: str):
        """
        Get the ERC20 token balance of the POL contract

        Parameters
        ----------
        tkn: str
            The token address

        Returns
        -------
        int
            The token balance

        """

        tkn_contract = self.mgr.get_or_create_token_contracts(self.mgr.web3, self.mgr.erc20_contracts, self.mgr.web3.toChecksumAddress(tkn))
        return tkn_contract.functions.balanceOf(self.mgr.cfg.BANCOR_V3_VAULT).call()


    def generate_shutdown_tx(self, tkn: str):
        """
        :param tkn: the token of the pool to shut down.

        Generates and submits the pool shutdown transaction
        """
        # Get current base fee for pending block
        gas_price = self.mgr.web3.eth.getBlock("pending").get("baseFeePerGas")
        # Get the current recommended priority fee from Alchemy, and increase it by our offset
        max_priority_gas = int(self.tx_helpers.get_max_priority_fee_per_gas_alchemy() * self.mgr.cfg.DEFAULT_GAS_PRICE_OFFSET)
        transaction = self.build_transaction(tkn=tkn, gas_price=gas_price, max_priority_gas=max_priority_gas, nonce=self.tx_helpers.get_nonce())
        return self.tx_helpers.submit_private_transaction(arb_tx=transaction, block_number=self.mgr.web3.eth.block_number) if transaction is not None else None


    def build_transaction(self, tkn, gas_price, max_priority_gas, nonce):
        """
        Handles the transaction generation


        returns:
            Returns a transaction ready to be submitted
        """

        try:
            return self.bancor_network_contract.functions.withdrawPOL(self.mgr.web3.toChecksumAddress(tkn)).build_transaction(self.tx_helpers.build_tx(
                            base_gas_price=gas_price, max_priority_fee=max_priority_gas, nonce=nonce
                        )
                    )
        except Exception as e:
            self.mgr.cfg.logger.debug(f"Error when building transaction: {e.__class__.__name__} {e}")
            if "max fee per gas less than block base fee" in str(e):
                try:
                    message = str(e)
                    split1 = message.split('maxFeePerGas: ')[1]
                    split2 = split1.split(' baseFee: ')
                    split_baseFee = int(int(split2[1].split(" (supplied gas")[0]))
                    split_maxPriorityFeePerGas = int(int(split2[0]) * self.mgr.cfg.DEFAULT_GAS_PRICE_OFFSET)
                    return self.bancor_network_contract.functions.withdrawPOL(
                        self.mgr.web3.toChecksumAddress(tkn)).build_transaction(self.tx_helpers.build_tx(
                            base_gas_price=split_baseFee,
                            max_priority_fee=split_maxPriorityFeePerGas,
                            nonce=nonce
                        )
                        )
                except Exception as e:
                    self.mgr.cfg.logger.debug(
                        f"(***2***) Error when building transaction: {e.__class__.__name__} {e}")
                    return None
