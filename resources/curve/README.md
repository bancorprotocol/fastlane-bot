## Abstract

This module supports calculating swap output on each one of [these pools](factory/Main.py#L16-L40), in each one of the following manners:
1. Before submitting swap-calculation requests, the user provides the current state of the pool (i.e., no onchain interactions)
2. Before submitting swap-calculation requests, the module fetches the current state of the pool (i.e., one onchain interaction)
3. For every swap-calculation request, the module calls the contract function onchain (i.e., one onchain interaction per request)

An example implementation of option 1 can be found in [test_offchain.py](test_offchain.py).

An example implementation of options 2 and 3 can be found in [test_onchain.py](test_onchain.py).

In order to use option 1, some level of acquaintance with the internal details of Curve Pools is required.

An example of these details can be found in [mock_pools.py](mock_pools.py) and fetched using [read_pools.py](read_pools.py).

## Prerequisites

- `python 3.9.13`
- `web3.py 6.9.0`

## Testing Pools

- `python test_offchain.py`
- `python test_onchain.py <HTTP Provider URL>`

## Reading Pools

- `python read_pools.py <HTTP Provider URL>`
