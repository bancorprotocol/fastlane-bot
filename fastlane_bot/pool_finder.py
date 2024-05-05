"""
Finds liquidity pools.

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from collections import defaultdict

from typing import List, Tuple, Dict, Any

from fastlane_bot.config.constants import ZERO_ADDRESS, UNISWAP_V2_NAME, UNISWAP_V3_NAME, SOLIDLY_V2_NAME
from fastlane_bot.config.multicaller import MultiCaller
from fastlane_bot.events.exchanges.base import Exchange

class PoolFinder:
    """A class that provides methods to find unsupported carbon pairs and triangles
        within a given set of flashloan tokens and external pairs.
    """

    multicallers = []

    def __init__(self, uni_v2_forks: List[str], uni_v3_forks: List[str], solidly_v2_forks: List[str], carbon_forks: List[str], flashloan_tokens: List[str]):
        self.uni_v2_forks = uni_v2_forks
        self.uni_v3_forks = uni_v3_forks
        self.solidly_v2_forks = solidly_v2_forks
        self.carbon_forks = carbon_forks
        self.flashloan_tokens = flashloan_tokens
        self.uni_v3_fee_tiers = defaultdict(set)
        self.carbon_pairs_seen = set()

    def init_exchanges(self, exchanges: List[Exchange], web3: Any, multicall_address: str):
        """ This function initializes multicallers that will be used for each exchange.

        The function is separated from the main __init__ function to enable easier testing.

        Args:
            exchanges (List[Exchange]): List of exchange objects for which to make multicalls.
            web3 (Web3): Web3 object
            multicall_address (str): The address of the multicall contract.


        """
        self.multicallers = {ex_name: {"multicaller": MultiCaller(contract=exchange.sync_factory_contract, web3=web3, multicall_address=multicall_address), "exchange": exchange} for ex_name, exchange in exchanges.items() if ex_name in self.uni_v2_forks + self.uni_v3_forks + self.solidly_v2_forks}

    def extract_univ3_fee_tiers(self, pools: List[Dict[str, Any]]):
        """
        Extracts unique fee tiers for each exchange listed under Uniswap V3 forks from the provided pool data.

        Args:
            pools (List[Dict[str, Any]]): List of pool dictionaries containing 'exchange_name' and 'fee'.

        This function updates the 'uni_v3_fee_tiers' dictionary where each exchange name is mapped to a set of unique fees.
        """
        for pool in pools:
            if pool["exchange_name"] in self.uni_v3_forks:
                self.uni_v3_fee_tiers[pool["exchange_name"]].add(int(pool["fee"]))


    def get_pools_for_unsupported_pairs(self, pools: List[Dict[str, Any]], arb_mode: str):
        """
        Main flow for Poolfinder.

        Args:
            pools (List[Dict[str, Any]]): A list of pool data where each pool is a dictionary. The expected keys in
                                      each dictionary should align with the requirements of the _extract_pairs,
                                      _find_unsupported_pairs, and _find_unsupported_triangles methods.

        Returns:
            Dict: Returns a dictionary with pools sorted into different exchange types (Uni V2 forks, Uni V3 forks,
                  and Solidly V2 forks), each associated with their specific supporting pools based on the unsupported
                  configurations identified.
        """
        carbon_pairs, other_pairs = self._extract_pairs(pools=pools, carbon_forks=self.carbon_forks)
        if not carbon_pairs:
            return [], [], []
        self.extract_univ3_fee_tiers(pools)
        func = PoolFinder._find_unsupported_triangles if arb_mode in ["triangle", "multi_triangle"] else PoolFinder._find_unsupported_pairs
        unsupported = func(self.flashloan_tokens, carbon_pairs=carbon_pairs, external_pairs=other_pairs)
        supporting_pools = self._find_pools(unsupported)
        return self._sort_exchange_pools(supporting_pools, self.uni_v2_forks, self.uni_v3_forks, self.solidly_v2_forks)


    def _find_pools(self, unsupported_pairs: List[Tuple]) -> Dict[str, List[str]]:
        """
            Collects pool addresses for each exchange, based on a set of unsupported token pairs
            and flashloan tokens. The function constructs pairs of tokens from unsupported_pairs with each
            flashloan token and retrieves pool data via multicall. It filters out invalid addresses.

            Args:
                unsupported_pairs (List[Tuple]): A list of tuples, where each tuple contains two token addresses.
                flashloan_tokens (List[str]): A list of token addresses available for flashloans.

            Returns:
                Dict[str, List[str]]: A list of dictionaries, where each dictionary maps an exchange's name
                                            to a list of valid pool addresses (i.e., non-zero addresses) obtained
                                            from the multicall across all generated pairs.

            Raises:
                Exception: An exception could be raised from the multicall operation depending on the
                           implementation specifics of the multicall context manager or the exchange's
                           get_pool_function method if it encounters a problem.
            """
        pairs = [(tkn, token) for pair in unsupported_pairs for tkn in pair for token in self.flashloan_tokens]

        result_list = {}
        for ex_name, ex_data in self.multicallers.items():
            mc = ex_data["multicaller"]
            ex = ex_data["exchange"]
            with mc:
                for pair in pairs:
                    if ex.base_exchange_name == UNISWAP_V2_NAME:
                        mc.add_call(ex.get_pool_function(ex.sync_factory_contract), pair[0], pair[1])
                    elif ex.base_exchange_name == UNISWAP_V3_NAME:
                        for fee in self.uni_v3_fee_tiers[ex.exchange_name]:
                            mc.add_call(ex.get_pool_function(ex.sync_factory_contract), pair[0], pair[1], fee)
                    elif ex.base_exchange_name == SOLIDLY_V2_NAME:
                        mc.add_call(ex.get_pool_function(ex.sync_factory_contract), *ex.get_pool_args(pair[0], pair[1], False))
                results = mc.multicall()
                result_list[ex.exchange_name] = [mc.web3.to_checksum_address(addr) for addr in results if addr != ZERO_ADDRESS]
        return result_list

    @staticmethod
    def _sort_exchange_pools(ex_pools: Dict, uni_v2_forks: List[str], uni_v3_forks: List[str], solidly_v2_forks: List[str]):
        """
        Categorizes pools based on the type of exchange they belong to into separate dictionaries.

        Args:
            ex_pools (List[Dict]): A list of dictionary where keys are exchange names and values are lists of pool addresses.

        Returns:
            Tuple[Dict, Dict, Dict]: Three dictionaries categorizing pool addresses into Uniswap V2 forks,
                                     Uniswap V3 forks, and Solidly V2 forks.
        """
        # Initialize separate dictionaries for each type of exchange fork
        uni_v2_pools = {}
        uni_v3_pools = {}
        solidly_v2_pools = {}

        # Assign pools to the appropriate category based on the exchange type
        for ex_name, pools in ex_pools.items():
            if ex_name in uni_v2_forks:
                target_pools = uni_v2_pools
            elif ex_name in uni_v3_forks:
                target_pools = uni_v3_pools
            elif ex_name in solidly_v2_forks:
                target_pools = solidly_v2_pools
            else:
                continue  # Skip exchanges that do not match any known category

            for addr in pools:
                target_pools[addr] = ex_name  # Map pool address to exchange name

        return uni_v2_pools, uni_v3_pools, solidly_v2_pools


    def _extract_pairs(self, pools: List[Dict[str, Any]], carbon_forks: List[str]) -> (List, set):
        """
        Extracts unique, order-insensitive pairs of tokens from pools, categorizing them
        into carbon pairs and other pairs based on the exchange's presence in carbon_forks.

        Args:
            pools (List[Dict[str, Any]]): List of pool dictionaries containing token addresses and exchange names.
            carbon_forks (List[str]): List of exchange names categorized under carbon forks.

        Returns:
            tuple: Two sets of unique token pairs, one for carbon forks and one for other exchanges.
        """
        carbon_pairs = set()
        other_pairs = set()

        for pool in pools:
            # Create a frozenset for each pair to ensure the pair is treated as order-insensitive
            pair = (pool["tkn0_address"], pool["tkn1_address"])
            frozen_pair = frozenset(pair)

            if pool["exchange_name"] in carbon_forks and frozen_pair not in self.carbon_pairs_seen:
                carbon_pairs.add(pair)
                self.carbon_pairs_seen.add(frozen_pair)
            else:
                other_pairs.add(pair)

        return list(carbon_pairs), other_pairs

    @staticmethod
    def _find_unsupported_triangles(flashloan_tokens: List[str], carbon_pairs: List[Tuple], external_pairs: set) -> List[Tuple]:
        """
        Identifies carbon pairs that cannot form a valid triangle with any of the flashloan tokens,
        even though each side of the pair is supported externally.

        Args:
            flashloan_tokens (List[str]): Tokens available for forming triangles.
            carbon_pairs (List[Tuple]): Carbon pairs to check for triangle support.
            external_pairs (List[Tuple[str, str]]): Pairs that are supported externally.

        Returns:
            List[Tuple]: List of carbon pairs that cannot form a valid triangle.
        """
        unsupported_triangles = []

        for pair in carbon_pairs:
            tkn0, tkn1 = pair[0], pair[1]
            if not any((frozenset((tkn0, tkn)) in external_pairs and frozenset((tkn1, tkn)) in external_pairs) for tkn in flashloan_tokens):
                unsupported_triangles.append(pair)
        return unsupported_triangles

    @staticmethod
    def _find_unsupported_pairs(flashloan_tokens: List[str], carbon_pairs: set, external_pairs: set):
        """
        Determines which carbon pairs are unsupported based on the lack of token support and non-existence in external pairs.

        Args:
            flashloan_tokens (List[str]): List of tokens supported for flashloans.
            carbon_pairs (List[Tuple]): Carbon pairs to evaluate for support.
            external_pairs (List[Tuple]): Pairs externally supported.

        Returns:
            List[Tuple]: List of unsupported carbon pairs.
        """
        unsupported_pairs = []
        for pair in carbon_pairs:
            tkn0, tkn1 = pair[0], pair[1]
            if (tkn0 not in flashloan_tokens and tkn1 not in flashloan_tokens):
                unsupported_pairs.append(pair)
                continue
            if pair not in external_pairs:
                unsupported_pairs.append(pair)

        return unsupported_pairs



