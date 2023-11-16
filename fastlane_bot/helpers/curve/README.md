## Abstract

This module supports calculating swap output on each one of [these pools](factory/Main.py#L17-L43), in each one of the following manners:
1. Before submitting swap-calculation requests, the user provides the current state of the pool (i.e., no onchain interactions)
2. Before submitting swap-calculation requests, the module fetches the current state of the pool (i.e., one onchain interaction)
3. For every swap-calculation request, the module calls the contract function onchain (i.e., one onchain interaction per request)

The following diagram illustrates the various different ways in which this module can be used (onchain interactions are marked `*`):
```
       make_pool
      /         \
     /           \
    /             \
   v               v
mock             * read *
    \             /    \
     \           /      \
      \         /        \
       v       v          v
       swap_calc        * swap_read *
```

The optional modes of operation described above are:
1. `make_pool --> mock --> swap_calc` (see an example in [test1.py](test1.py))
2. `make_pool --> read --> swap_calc` (see an example in [test2.py](test2.py))
3. `make_pool --> read --> swap_read` (see an example in [test3.py](test3.py))

In order to use option 1, some level of acquaintance with the internal details of Curve Pools is required.

An example of these details can be found in [example.py](example.py) and fetched using [read_pools.py](read_pools.py).

## Prerequisites

- `python 3.9.13`
- `web3.py 6.9.0`

## Testing Pools

- `python test1.py`
- `python test2.py <HTTP Provider URL>`
- `python test3.py <HTTP Provider URL>`

## Reading Pools

- `python read_pools.py <HTTP Provider URL>`
