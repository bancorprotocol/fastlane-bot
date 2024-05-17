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
    def __init__(
        self,
        carbon_forks: List[str],
        uni_v3_forks: List[str],
        flashloan_tokens: List[str],
        exchanges: List[Exchange],
        web3: Any,
        multicall_address: str
    ):
        self._carbon_forks = carbon_forks
        self._uni_v3_forks = uni_v3_forks
        self._flashloan_tokens = flashloan_tokens
        self._uni_v3_fee_tiers = defaultdict(set)
        self._carbon_pairs_seen = set()

        self._exchanges = list(filter(lambda e: e.base_exchange_name in [UNISWAP_V2_NAME, UNISWAP_V3_NAME, SOLIDLY_V2_NAME], exchanges.values()))
        self._web3 = web3
        self._multicall_address = multicall_address

    def extract_univ3_fee_tiers(self, pools: List[Dict[str, Any]]):
        """
        Extracts unique fee tiers for each exchange listed under Uniswap V3 forks from the provided pool data.

        Args:
            pools (List[Dict[str, Any]]): List of pool dictionaries containing 'exchange_name' and 'fee'.

        This function updates the 'uni_v3_fee_tiers' dictionary where each exchange name is mapped to a set of unique fees.
        """
        for pool in pools:
            if pool["exchange_name"] in self._uni_v3_forks:
                self._uni_v3_fee_tiers[pool["exchange_name"]].add(int(pool["fee"]))


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
        carbon_pairs, other_pairs = self._extract_pairs(pools=pools)
        if not carbon_pairs:
            return [], [], []
        self.extract_univ3_fee_tiers(pools)  # TODO: these should be configured per exchange
        if arb_mode in ["triangle", "multi_triangle"]:
            unsupported_pairs = PoolFinder._find_unsupported_triangles(self._flashloan_tokens, carbon_pairs=carbon_pairs, external_pairs=other_pairs)
        else:
            unsupported_pairs = PoolFinder._find_unsupported_pairs(self._flashloan_tokens, carbon_pairs=carbon_pairs, external_pairs=other_pairs)
        missing_pools = self._find_pools(unsupported_pairs)
        return missing_pools[UNISWAP_V2_NAME], missing_pools[UNISWAP_V3_NAME], missing_pools[SOLIDLY_V2_NAME]


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
        pairs = [(tkn, token) for pair in unsupported_pairs for tkn in pair for token in self._flashloan_tokens]
        chunk_size = 400
        # Create the list of chunks
        chunked_pairs = [pairs[i:i + chunk_size] for i in range(0, len(pairs), chunk_size)]
        result = defaultdict(dict)

        for exchange in self._exchanges:
            for pair_chunk in chunked_pairs:
                mc = MultiCaller(contract=exchange.sync_factory_contract, web3=self._web3, multicall_address=self._multicall_address)
                for pair in pair_chunk:
                    if exchange.base_exchange_name == UNISWAP_V2_NAME:
                        mc.add_call(exchange.get_pool_function(exchange.sync_factory_contract), pair[0], pair[1])
                    elif exchange.base_exchange_name == UNISWAP_V3_NAME:
                        for fee in self._uni_v3_fee_tiers[exchange.exchange_name]:
                            mc.add_call(exchange.get_pool_function(exchange.sync_factory_contract), pair[0], pair[1], fee)
                    elif exchange.base_exchange_name == SOLIDLY_V2_NAME:
                        mc.add_call(exchange.get_pool_function(exchange.sync_factory_contract), *exchange.get_pool_args(pair[0], pair[1], False))
                response = mc.multicall()
                result[exchange.base_exchange_name] = {
                    mc.web3.to_checksum_address(addr): exchange.exchange_name
                    for addr
                    in response
                    if addr != ZERO_ADDRESS
                }
        return result


    def _extract_pairs(self, pools: List[Dict[str, Any]]) -> Tuple[List, set]:
        """
        Extracts unique, order-insensitive pairs of tokens from pools, categorizing them
        into carbon pairs and other pairs based on the exchange's presence in carbon_forks.

        Args:
            pools (List[Dict[str, Any]]): List of pool dictionaries containing token addresses and exchange names.

        Returns:
            tuple: Two sets of unique token pairs, one for carbon forks and one for other exchanges.
        """
        carbon_pairs = set()
        other_pairs = set()

        for pool in pools:
            # Create a frozenset for each pair to ensure the pair is treated as order-insensitive
            pair = (pool["tkn0_address"], pool["tkn1_address"])

            if pool["exchange_name"] in self._carbon_forks:
                frozen_pair = frozenset(pair)
                if frozen_pair not in self._carbon_pairs_seen:
                    carbon_pairs.add(pair)
                    self._carbon_pairs_seen.add(frozen_pair)
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
    def _find_unsupported_pairs(flashloan_tokens: List[str], carbon_pairs: List[Tuple], external_pairs: set):
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
            elif pair not in external_pairs:
                unsupported_pairs.append(pair)

        return unsupported_pairs
