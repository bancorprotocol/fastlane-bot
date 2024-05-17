# ------------------------------------------------------------
# Auto generated test file `test_907_RuntimeParameters.py`
# ------------------------------------------------------------
# source file   = NBTest_907_RuntimeParameters.py
# test id       = 907
# test comment  = RuntimeParameters
# ------------------------------------------------------------


import sys
from contextlib import redirect_stderr
from unittest import mock

import pytest

from fastlane_bot.tools.cpc import T
from main import main  # adjust import according to your script's location and name

@pytest.fixture
def mock_args():
    class Args:
        def __init__(self):
            self.cache_latest_only = 'True'
            self.backdate_pools = 'True'
            self.static_pool_data_filename = "static_pool_data"
            self.arb_mode = "multi_pairwise_all"
            self.flashloan_tokens = "LINK,ETH,BNT,WBTC,DAI,USDC,USDT,WETH"  # Assuming T.LINK, etc. are constants defined elsewhere
            self.n_jobs = -1
            self.exchanges = "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3"
            self.polling_interval = 1
            self.alchemy_max_block_fetch = 2000
            self.reorg_delay = 0
            self.logging_path = ""
            self.loglevel = "INFO"
            self.use_cached_events = 'False'
            self.run_data_validator = 'False'
            self.randomizer = "3"
            self.limit_bancor3_flashloan_tokens = 'True'
            self.default_min_profit_gas_token = "0.01"
            self.timeout = 1
            self.target_tokens = None
            self.replay_from_block = None
            self.tenderly_fork_id = None
            self.tenderly_event_exchanges = "pancakeswap_v2,pancakeswap_v3"
            self.increment_time = 1
            self.increment_blocks = 1
            self.blockchain = "ethereum"
            self.pool_data_update_frequency = -1
            self.use_specific_exchange_for_target_tokens = None
            self.prefix_path = ""
            self.self_fund = 'False'
            self.read_only = 'True'
            self.is_args_test = 'True'
            self.rpc_url = None

    return Args()


arb_mode_happy_path_options = [
    "multi_pairwise_all",
    "multi_triangle",
    "b3_two_hop",
]
alchemy_max_block_fetch_happy_path_options = [100, 2000, 3, 4, 5]
cache_latest_only_happy_path_options = ['True', 'False']
backdate_pools_happy_path_options = ['True', 'False']
flashloan_tokens_happy_path_options = [
    f"{T.LINK},{T.NATIVE_ETH}",
    f"{T.LINK},{T.NATIVE_ETH},{T.BNT}",
    f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC}",
    f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI}",
]
default_min_profit_gas_token_happy_path_options = ["0.01", 100, 2000, '3']
n_jobs_happy_path_options = [5, -1]
timeout_happy_path_options = [60, 100]
exchanges_happy_path_options = [
    "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2",
    "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3",
    "carbon_v1,bancor_v3,bancor_v2,bancor_pol",
    "carbon_v1,bancor_v3,bancor_v2",
    "carbon_v1,bancor_v3",
]
randomizer_happy_path_options = [1, '2']
blockchain_happy_path_options = ["ethereum", "coinbase_base"]

@pytest.mark.parametrize("arb_mode", arb_mode_happy_path_options)
def test_arb_mode(arb_mode, mock_args, capsys):
    mock_args.arb_mode = arb_mode
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"arb_mode: {arb_mode}" in output

@pytest.mark.parametrize("alchemy_max_block_fetch", alchemy_max_block_fetch_happy_path_options)
def test_alchemy_max_block_fetch(alchemy_max_block_fetch, mock_args, capsys):
    mock_args.alchemy_max_block_fetch = alchemy_max_block_fetch
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"alchemy_max_block_fetch: {alchemy_max_block_fetch}" in output

@pytest.mark.parametrize("cache_latest_only", cache_latest_only_happy_path_options)
def test_cache_latest_only(cache_latest_only, mock_args, capsys):
    mock_args.cache_latest_only = cache_latest_only
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"cache_latest_only: {cache_latest_only}" in output

@pytest.mark.parametrize("backdate_pools", backdate_pools_happy_path_options)
def test_backdate_pools(backdate_pools, mock_args, capsys):
    mock_args.backdate_pools = backdate_pools
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"backdate_pools: {backdate_pools}" in output

@pytest.mark.parametrize("flashloan_tokens", flashloan_tokens_happy_path_options)
def test_flashloan_tokens(flashloan_tokens, mock_args, capsys):
    mock_args.flashloan_tokens = flashloan_tokens
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"flashloan_tokens: {flashloan_tokens.split(',')}" in output

@pytest.mark.parametrize("default_min_profit_gas_token", default_min_profit_gas_token_happy_path_options)
def test_default_min_profit_gas_token(default_min_profit_gas_token, mock_args, capsys):
    mock_args.default_min_profit_gas_token = default_min_profit_gas_token
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"default_min_profit_gas_token: {default_min_profit_gas_token}" in output

@pytest.mark.parametrize("n_jobs", n_jobs_happy_path_options)
def test_n_jobs(n_jobs, mock_args, capsys):
    mock_args.n_jobs = n_jobs
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"n_jobs: {n_jobs}" in output

@pytest.mark.parametrize("timeout", timeout_happy_path_options)
def test_timeout(timeout, mock_args, capsys):
    mock_args.timeout = timeout
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"timeout: {timeout}" in output

@pytest.mark.parametrize("randomizer", randomizer_happy_path_options)
def test_randomizer(randomizer, mock_args, capsys):
    mock_args.randomizer = randomizer
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"randomizer: {randomizer}" in output

@pytest.mark.parametrize("blockchain", blockchain_happy_path_options)
def test_blockchain(blockchain, mock_args, capsys):
    mock_args.blockchain = blockchain
    with open('output.txt', 'w') as f:
        with redirect_stderr(f):
            main(mock_args)
    # read the console output
    with open('output.txt', 'r') as f:
        output = f.read()
    assert f"blockchain: {blockchain}" in output
