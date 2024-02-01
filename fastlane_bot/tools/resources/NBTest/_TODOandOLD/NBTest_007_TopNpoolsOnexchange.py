# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + jupyter={"outputs_hidden": true}
import requests

def get_top_n_pools_for_exchange(exchange_name: str, top_n: int = 200) -> list:
    """
    Fetches the top 5 pools from the given platform.

    Parameters
    ----------
    exchange_name : str
        The exchange_name to fetch the top 5 pools from. Choose from 'uniswap_v2', 'uniswap_v3', or 'sushiswap'.
    top_n : int, optional
        The number of pools to fetch, by default 5

    Returns
    -------
    list
        A list of the top 5 pools from the given platform.
    """
    if exchange_name not in ["uniswap_v2", "uniswap_v3", "sushiswap"]:
        raise ValueError("Invalid platform. Choose from 'uniswap_v2', 'uniswap_v3', or 'sushiswap'.")

    if exchange_name == "uniswap_v2":
        url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
        query = """
        {
          pairs(first: top_n, orderBy: reserveUSD, orderDirection: desc) {
            id
            token0 {
              symbol
              id
            }
            token1 {
              symbol
              id
            }
          }
        }
        """.replace("top_n", str(top_n))
    elif exchange_name == "uniswap_v3":
        url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
        query = """
        {
          pools(first: top_n, orderBy: liquidity, orderDirection: desc) {
            id
            token0 {
              symbol
              id
            }
            token1 {
              symbol
              id
            }
          }
        }
        """.replace("top_n", str(top_n))
    elif exchange_name == "sushiswap":
        url = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"
        query = """
        {
          pairs(first: top_n, orderBy: reserveUSD, orderDirection: desc) {
            id
            token0 {
              symbol
              id
            }
            token1 {
              symbol
              id
            }
          }
        }
        """.replace("top_n", str(top_n))

    response = requests.post(url, json={'query': query})
    data = response.json()

    if "errors" in data:
        raise Exception("Error in fetching data from TheGraph API")

    pairs = data["data"]["pairs"] if exchange_name != "uniswap_v3" else data["data"]["pools"]

    pair_info = []
    for pair in pairs:
        pool_address = pair["id"]
        tkn0_key = f"{pair['token0']['symbol']}-{pair['token0']['id'][-4:]}"
        tkn1_key = f"{pair['token1']['symbol']}-{pair['token1']['id'][-4:]}"
        pair_name = f"{tkn0_key}/{tkn1_key}"
        pair_info.append({"pair_name": pair_name, "pool_address": pool_address})

    return pair_info

top_5_uniswap_v2_pairs = get_top_n_pools_for_exchange("uniswap_v2")
top_5_uniswap_v3_pairs = get_top_n_pools_for_exchange("uniswap_v3")
top_5_sushiswap_pairs = get_top_n_pools_for_exchange("sushiswap")



print("Top 5 Uniswap v2 pairs:", top_5_uniswap_v2_pairs)
print("Top 5 Uniswap v3 pairs:", top_5_uniswap_v3_pairs)
print("Top 5 SushiSwap pairs:", top_5_sushiswap_pairs)

# + jupyter={"outputs_hidden": false}
import pytest
from unittest.mock import MagicMock
import requests

def test_invalid_platform():
    with pytest.raises(ValueError):
        get_top_n_pools_for_exchange("invalid_platform")

def test_uniswap_v2_pools():
    requests.post = MagicMock(return_value=MagicMock(json=lambda: {"data": {"pairs": []}}))
    try:
        pairs = get_top_n_pools_for_exchange("uniswap_v2")
        assert pairs is not None
    except Exception as e:
        pytest.fail(f"get_top_5_pools raised an exception: {e}")

def test_uniswap_v3_pools():
    requests.post = MagicMock(return_value=MagicMock(json=lambda: {"data": {"pools": []}}))
    try:
        pairs = get_top_n_pools_for_exchange("uniswap_v3")
        assert pairs is not None
    except Exception as e:
        pytest.fail(f"get_top_5_pools raised an exception: {e}")

def test_sushiswap_pools():
    requests.post = MagicMock(return_value=MagicMock(json=lambda: {"data": {"pairs": []}}))
    try:
        pairs = get_top_n_pools_for_exchange("sushiswap")
        assert pairs is not None
    except Exception as e:
        pytest.fail(f"get_top_5_pools raised an exception: {e}")


test_invalid_platform()
test_uniswap_v2_pools()
test_uniswap_v3_pools()
test_sushiswap_pools()
