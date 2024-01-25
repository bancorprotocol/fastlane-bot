import os
import subprocess

import pytest

from fastlane_bot.tools.cpc import T


def find_main_py():
    # Start at the directory of the current script
    cwd = os.path.abspath(os.path.join(os.getcwd()))
    while True:
        if "main.py" in os.listdir(cwd):
            return cwd  # Found the directory containing main.py
        # If not, go up one directory
        new_cwd = os.path.dirname(cwd)

        # If we're already at the root directory, stop searching
        if new_cwd == cwd:
            raise FileNotFoundError("Could not find main.py in any parent directory")

        cwd = new_cwd


main_script_path = find_main_py()
arb_mode_happy_path_options = [
    "single",
    "multi",
    "triangle",
    "multi_triangle",
    "b3_two_hop",
]
arb_mode_invalid_options = ["s", "m", "t", None, 3]
alchemy_max_block_fetch_happy_path_options = [100, 2000, 3, 4, 5]
alchemy_max_block_fetch_invalid_options = [None, 3.5, "a", "b", "c"]
cache_latest_only_happy_path_options = [True, False, True, False, True]
cache_latest_only_invalid_options = [None, 3.5, "a", "b", "c"]
backdate_pools_happy_path_options = [True, False, True, False, True]
backdate_pools_invalid_options = [None, 3.5, "a", "b", "c"]
flashloan_tokens_happy_path_options = [
    f"{T.LINK},{T.NATIVE_ETH}",
    f"{T.LINK},{T.NATIVE_ETH},{T.BNT}",
    f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC}",
    f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI}",
]
flashloan_tokens_invalid_options = [
    None,
    3.5,
    "a",
    "b",
    "c",
    f"",
]
default_min_profit_gas_token_happy_path_options = [60, 100, 2000, 3, 4]
default_min_profit_gas_token_invalid_options = [None, "a", "b", "c"]
n_jobs_happy_path_options = [2, 3, 4, 5, -1]
n_jobs_invalid_options = [None, 3.5, "a", "b", "c"]
timeout_happy_path_options = [60, 100, 3, 4]
timeout_invalid_options = [None, 3.5, "a", "b", "c"]
exchanges_happy_path_options = [
    "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2",
    "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3",
    "carbon_v1,bancor_v3,bancor_v2,bancor_pol",
    "carbon_v1,bancor_v3,bancor_v2",
    "carbon_v1,bancor_v3",
]
exchanges_invalid_options = [
    None,
    3.5,
    "a",
    "b",
    "c",
    f"",
]
randomizer_happy_path_options = [1, 2, 3, 4, 5]
randomizer_invalid_options = [None, 3.5, "a", "b", "c"]
blockchain_happy_path_options = ["ethereum", "coinbase_base"]
blockchain_invalid_options = ["arbitrum", "polygon"]


@pytest.mark.parametrize("arb_mode", arb_mode_happy_path_options)
def test_arb_mode_happy_path_options(arb_mode):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--arb_mode={arb_mode}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"arb_mode: {arb_mode}" in result.stderr


@pytest.mark.parametrize("arb_mode", arb_mode_invalid_options)
def test_arb_mode_invalid_options(arb_mode):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--arb_mode={arb_mode}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert f"error: argument --arb_mode: invalid choice: '{arb_mode}'" in str(e)


@pytest.mark.parametrize(
    "alchemy_max_block_fetch", alchemy_max_block_fetch_happy_path_options
)
def test_alchemy_max_block_fetch(alchemy_max_block_fetch):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--alchemy_max_block_fetch={alchemy_max_block_fetch}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"alchemy_max_block_fetch: {alchemy_max_block_fetch}" in result.stderr


@pytest.mark.parametrize(
    "alchemy_max_block_fetch", alchemy_max_block_fetch_invalid_options
)
def test_alchemy_max_block_fetch_invalid_options(alchemy_max_block_fetch):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--alchemy_max_block_fetch={alchemy_max_block_fetch}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert (
                f"error: argument --alchemy_max_block_fetch: invalid int value: '{alchemy_max_block_fetch}'"
                in str(e)
        )


@pytest.mark.parametrize("cache_latest_only", cache_latest_only_happy_path_options)
def test_cache_latest_only(cache_latest_only):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--cache_latest_only={cache_latest_only}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"cache_latest_only: {cache_latest_only}" in result.stderr


@pytest.mark.parametrize("cache_latest_only", cache_latest_only_invalid_options)
def test_cache_latest_only_invalid_options(cache_latest_only):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--cache_latest_only={cache_latest_only}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert (
                f"error: argument --cache_latest_only: invalid choice: '{cache_latest_only}'"
                in str(e)
        )


@pytest.mark.parametrize("backdate_pools", backdate_pools_happy_path_options)
def test_backdate_pools(backdate_pools):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--backdate_pools={backdate_pools}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"backdate_pools: {backdate_pools}" in result.stderr


@pytest.mark.parametrize("backdate_pools", backdate_pools_invalid_options)
def test_backdate_pools_invalid_options(backdate_pools):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--backdate_pools={backdate_pools}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert (
                f"error: argument --backdate_pools: invalid choice: '{backdate_pools}'"
                in str(e)
        )


@pytest.mark.parametrize("flashloan_tokens", flashloan_tokens_happy_path_options)
def test_flashloan_tokens(flashloan_tokens):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--flashloan_tokens={flashloan_tokens}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"flashloan_tokens: {flashloan_tokens.split(',')}" in result.stderr


@pytest.mark.parametrize(
    "default_min_profit_gas_token", default_min_profit_gas_token_happy_path_options
)
def test_default_min_profit_gas_token(default_min_profit_gas_token):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--default_min_profit_gas_token={default_min_profit_gas_token}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert (
            f"default_min_profit_gas_token: {default_min_profit_gas_token}" in result.stderr
    )


@pytest.mark.parametrize(
    "default_min_profit_gas_token", default_min_profit_gas_token_invalid_options
)
def test_default_min_profit_gas_token_invalid_options(default_min_profit_gas_token):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--default_min_profit_gas_token={default_min_profit_gas_token}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert (
                f"error: argument --default_min_profit_gas_token: invalid int value: '{default_min_profit_gas_token}'"
                in str(e)
        )


@pytest.mark.parametrize("n_jobs", n_jobs_happy_path_options)
def test_n_jobs(n_jobs):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--n_jobs={n_jobs}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"n_jobs: {n_jobs}" in result.stderr


@pytest.mark.parametrize("n_jobs", n_jobs_invalid_options)
def test_n_jobs_invalid_options(n_jobs):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--n_jobs={n_jobs}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert f"error: argument --n_jobs: invalid int value: '{n_jobs}'" in str(e)


@pytest.mark.parametrize("timeout", timeout_happy_path_options)
def test_timeout(timeout):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--timeout={timeout}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"timeout: {timeout}" in result.stderr


@pytest.mark.parametrize("timeout", timeout_invalid_options)
def test_timeout_invalid_options(timeout):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--timeout={timeout}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert f"error: argument --timeout: invalid int value: '{timeout}'" in str(e)


@pytest.mark.parametrize("exchanges", exchanges_happy_path_options)
def test_exchanges(exchanges):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--exchanges={exchanges}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"exchanges: {exchanges.split(',')}" in result.stderr


@pytest.mark.parametrize("randomizer", randomizer_happy_path_options)
def test_randomizer(randomizer):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--randomizer={randomizer}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"randomizer: {randomizer}" in result.stderr


@pytest.mark.parametrize("randomizer", randomizer_invalid_options)
def test_randomizer_invalid_options(randomizer):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--randomizer={randomizer}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert (
                f"error: argument --randomizer: invalid int value: '{randomizer}'" in str(e)
        )


@pytest.mark.parametrize("blockchain", blockchain_happy_path_options)
def test_blockchain(blockchain):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--blockchain={blockchain}",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=5)
    assert f"blockchain: {blockchain}" in result.stderr


@pytest.mark.parametrize("blockchain", blockchain_invalid_options)
def test_blockchain_invalid_options(blockchain):
    cmd = [
        "python",
        f"{main_script_path}/main.py",
        "--is_args_test=True",
        f"--blockchain={blockchain}",
    ]
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = subprocess.run(
            cmd, text=True, stderr=1, stdout=1, check=True, timeout=5
        )
        assert f"error: argument --blockchain: invalid choice: '{blockchain}'" in str(e)
