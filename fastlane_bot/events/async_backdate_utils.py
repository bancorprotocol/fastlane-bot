"""
[DOC-TODO-short description of what the file does, max 80 chars]

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import asyncio
import time
from typing import Any, Dict, Tuple, List
from web3 import AsyncWeb3

from fastlane_bot.events.utils import parse_non_multicall_rows_to_update


async def async_main_backdate_from_contracts(c: List[Dict[str, Any]], w3_async: AsyncWeb3) -> Tuple[Any]:
    return await asyncio.wait_for(
        asyncio.gather(
            *[async_handle_main_backdate_from_contracts(**args, w3_async=w3_async) for args in c]
        ),
        timeout=20 * 60,
    )


def async_backdate_from_contracts(mgr: Any, rows: List[int]):
    abis = {exchange_name: exchange.get_abi() for exchange_name, exchange in mgr.exchanges.items()}
    contracts = get_backdate_contracts(abis, mgr, rows)
    chunks = [contracts[i : i + 1000] for i in range(0, len(contracts), 1000)]
    for chunk in chunks:
        loop = asyncio.get_event_loop()
        vals = loop.run_until_complete(async_main_backdate_from_contracts(chunk, w3_async=mgr.w3_async))
        idxes = [val[0] for val in vals]
        updated_pool_info = [val[1] for val in vals]
        for i, idx in enumerate(idxes):
            updated_pool_data = updated_pool_info[i]
            mgr.pool_data[idx] = updated_pool_data


def get_backdate_contracts(
    abis: Dict, mgr: Any, rows: List[int]
) -> List[Dict[str, Any]]:
    contracts = []
    for idx in rows:
        pool_info = mgr.pool_data[idx]
        contracts.append(
            {
                "idx": idx,
                "pool": mgr.get_or_init_pool(pool_info),
                "w3_tenderly": mgr.w3_tenderly,
                "tenderly_fork_id": mgr.tenderly_fork_id,
                "pool_info": pool_info,
                "contract": mgr.w3_async.eth.contract(
                    address=mgr.pool_data[idx]["address"],
                    abi=abis[mgr.pool_data[idx]["exchange_name"]],
                ),
            }
        )
    return contracts


async def async_handle_main_backdate_from_contracts(
    idx: int,
    pool: Any,
    w3_tenderly: Any,
    w3_async: AsyncWeb3,
    tenderly_fork_id: str,
    pool_info: Dict,
    contract: Any,
) -> Tuple[int, Dict[str, Any]]:
    params = await pool.async_update_from_contract(
        contract,
        tenderly_fork_id=tenderly_fork_id,
        w3_tenderly=w3_tenderly,
        w3=w3_async,
    )
    for key, value in params.items():
        pool_info[key] = value
    return idx, pool_info


def async_handle_initial_iteration(
    backdate_pools: bool,
    last_block: int,
    mgr: Any,
    start_block: int,
    current_block: int,
):
    if last_block == 0:
        non_multicall_rows_to_update = mgr.get_rows_to_update(start_block)

        if backdate_pools:
            # Remove duplicates
            non_multicall_rows_to_update = list(set(non_multicall_rows_to_update))

            # Parse the rows to update
            other_pool_rows = parse_non_multicall_rows_to_update(
                mgr, non_multicall_rows_to_update
            )

            mgr.cfg.logger.info(
                f"Backdating {len(other_pool_rows)} pools from {start_block} to {current_block}"
            )
            start_time = time.time()
            async_backdate_from_contracts(
                mgr=mgr,
                rows=other_pool_rows,
            )
            mgr.cfg.logger.info(
                f"Backdating {len(other_pool_rows)} pools took {(time.time() - start_time):0.4f} seconds"
            )
