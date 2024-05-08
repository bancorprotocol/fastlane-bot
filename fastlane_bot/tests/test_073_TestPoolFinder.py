from fastlane_bot.pool_finder import PoolFinder


def test_find_unsupported_pairs():
    flashloan_tokens = ['TokenA', 'TokenB']
    carbon_pairs = [('TokenA', 'TokenC'), ('TokenC', 'TokenD'), ('TokenB', 'TokenE')]
    external_pairs = {frozenset(('TokenA', 'TokenB')), frozenset(('TokenC', 'TokenE'))}
    # Expected result
    # ('TokenA', 'TokenC') is supported by flashloan_tokens but not in external_pairs
    # ('TokenC', 'TokenD') is unsupported by flashloan_tokens and not in external_pairs
    # ('TokenB', 'TokenE') is supported by flashloan_tokens but not in external_pairs
    expected_result = [('TokenA', 'TokenC'), ('TokenC', 'TokenD'), ('TokenB', 'TokenE')]

    # Function under test
    result = PoolFinder._find_unsupported_pairs(flashloan_tokens, carbon_pairs, external_pairs)

    # Check that the function returns the correct list of unsupported pairs
    assert sorted(result) == sorted(expected_result)

def test_find_unsupported_triangles():
    flashloan_tokens = ['TokenA', 'TokenB']
    carbon_pairs = [('TokenA', 'TokenC'), ('TokenC', 'TokenD'), ('TokenB', 'TokenE')]
    external_pairs = {frozenset(('TokenA', 'TokenC')), frozenset(('TokenA', 'TokenD'))}
    # Expected result
    # ('TokenA', 'TokenC') is unsupported by triangles
    # ('TokenC', 'TokenD') is supported by triangles
    # ('TokenB', 'TokenE') is unsupported by triangles
    expected_result = [('TokenA', 'TokenC'), ('TokenB', 'TokenE')]

    # Function under test
    result = PoolFinder._find_unsupported_triangles(flashloan_tokens, carbon_pairs, external_pairs)

    # Check that the function returns the correct list of unsupported pairs
    assert len(expected_result) == len(result)
    assert sorted(expected_result) == sorted(result)


def test_extract_pairs():
    # Sample data for testing
    uni_v2_exchanges = ["bob_ex"]
    uni_v3_exchanges = ["fred_ex"]
    solidly_v2_exchanges = ["george_ex", "moose_ex"]
    flashloan_tokens = ["BNT"]
    pools = [
        {"exchange_name": "CarbonX", "tkn0_address": "WBTC", "tkn1_address": "BNT"},
        {"exchange_name": "CarbonX", "tkn0_address": "BNT", "tkn1_address": "WBTC"},  # Reverse order, should be treated as same
        {"exchange_name": "NonCarbon", "tkn0_address": "WETH", "tkn1_address": "USDT"},
        {"exchange_name": "NonCarbon", "tkn0_address": "USDC", "tkn1_address": "WBTC"},
        {"exchange_name": "CarbonX", "tkn0_address": "WETH", "tkn1_address": "USDC"}
    ]
    carbon_forks = ["CarbonX"]

    # Expected results
    expected_carbon_pairs = {frozenset(('WBTC', 'BNT')), frozenset(('WETH', 'USDC'))}
    expected_other_pairs = {frozenset(('WETH', 'USDT')), frozenset(('USDC', 'WBTC'))}
    #expected_carbon_pairs = [('WBTC', 'BNT'), ('WETH', 'USDC')]
    pool_finder = PoolFinder(uni_v2_forks=uni_v2_exchanges, uni_v3_forks=uni_v3_exchanges, solidly_v2_forks=solidly_v2_exchanges, carbon_forks=carbon_forks, flashloan_tokens=flashloan_tokens)

    # Call the function with test data
    carbon_pairs, other_pairs = pool_finder._extract_pairs(pools, carbon_forks)

    # Assert the results are as expected
    assert frozenset(carbon_pairs[0]) in expected_carbon_pairs
    assert frozenset(carbon_pairs[1]) in expected_carbon_pairs
    for _pair in other_pairs:
        assert frozenset(_pair) in expected_other_pairs
    #assert other_pairs == expected_other_pairs
    assert len(carbon_pairs) == 2
    assert len(other_pairs) == 2

def test_sort_exchanges():
    exchange_pools = {
        "bob_ex": ["1", "2", "3"],
        "fred_ex": ["4", "5"],
        "george_ex": ["6", "7", "8"],
        "moose_ex": ["9", "10", "11", "12"]
    }

    uni_v2_exchanges = ["bob_ex"]
    uni_v3_exchanges = ["fred_ex"]
    solidly_v2_exchanges = ["george_ex", "moose_ex"]
    uni_v2_pools, uni_v3_pools, solidly_v2_pools = PoolFinder._sort_exchange_pools(ex_pools=exchange_pools, uni_v2_forks=uni_v2_exchanges, uni_v3_forks=uni_v3_exchanges, solidly_v2_forks=solidly_v2_exchanges)


    assert len(uni_v2_pools.keys()) == 3
    assert len(uni_v3_pools.keys()) == 2
    assert len(solidly_v2_pools.keys()) == 7

    assert uni_v2_pools["1"] == "bob_ex"
    assert uni_v3_pools["5"] == "fred_ex"
    assert solidly_v2_pools["7"] == "george_ex"
    assert solidly_v2_pools["9"] == "moose_ex"





