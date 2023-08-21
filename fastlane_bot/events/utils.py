# coding=utf-8
"""
Contains the utils functions for events

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import json
import os
import time
from _decimal import Decimal
from typing import Any, Union, Dict, Set, List, Tuple, Hashable
from typing import List

import pandas as pd
from hexbytes import HexBytes
from joblib import Parallel, delayed
from web3.datastructures import AttributeDict

from fastlane_bot import Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.events.managers.manager import Manager


def filter_latest_events(
    mgr: Manager, events: List[List[AttributeDict]]
) -> List[AttributeDict]:
    """
    This function filters out the latest events for each pool. Given a nested list of events, it iterates through all events
    and keeps track of the latest event (i.e., with the highest block number) for each pool. The key used to identify each pool
    is derived from the event data using manager's methods.

    Args:
        mgr (Base): A Base object that provides methods to handle events and their related pools.
        events (List[List[AttributeDict]]): A nested list of events, where each event is an AttributeDict that includes
        the event data and associated metadata.

    Returns:
        List[AttributeDict]: A list of events, each representing the latest event for its corresponding pool.
    """
    latest_entry_per_pool = {}
    all_events = [event for event_list in events for event in event_list]

    # Handles the case where multiple pools are created in the same block
    all_events.reverse()

    for event in all_events:
        pool_type = mgr.pool_type_from_exchange_name(
            mgr.exchange_name_from_event(event)
        )
        if pool_type:
            key = pool_type.unique_key()
        else:
            continue
        if key == "cid":
            key = "id"
        elif key == "tkn1_address":
            if event["args"]["pool"] != mgr.cfg.BNT_ADDRESS:
                key = "pool"
            else:
                key = "tkn_address"
        unique_key = event[key] if key in event else event["args"][key]

        if unique_key in latest_entry_per_pool:
            if event["blockNumber"] > latest_entry_per_pool[unique_key]["blockNumber"]:
                latest_entry_per_pool[unique_key] = event
            elif (
                event["blockNumber"] == latest_entry_per_pool[unique_key]["blockNumber"]
            ):
                if (
                    event["transactionIndex"]
                    == latest_entry_per_pool[unique_key]["transactionIndex"]
                ):
                    if (
                        event["logIndex"]
                        > latest_entry_per_pool[unique_key]["logIndex"]
                    ):
                        latest_entry_per_pool[unique_key] = event
                elif (
                    event["transactionIndex"]
                    > latest_entry_per_pool[unique_key]["transactionIndex"]
                ):
                    latest_entry_per_pool[unique_key] = event
                else:
                    continue
            else:
                continue
        else:
            latest_entry_per_pool[unique_key] = event

    return list(latest_entry_per_pool.values())


def complex_handler(obj: Any) -> Union[Dict, str, List, Set, Any]:
    """
    This function aims to handle complex data types, such as web3.py's AttributeDict, HexBytes, and native Python collections
    like dict, list, tuple, and set. It recursively traverses these collections and converts their elements into more "primitive"
    types, making it easier to work with these elements or serialize the data into JSON.

    Args:
        obj (Any): The object to be processed. This can be of any data type, but the function specifically handles AttributeDict,
        HexBytes, dict, list, tuple, and set.

    Returns:
        Union[Dict, str, List, Set, Any]: Returns a "simplified" version of the input object, where AttributeDict is converted
        into dict, HexBytes into str, and set into list. For dict, list, and tuple, it recursively processes their elements.
        If the input object does not match any of the specified types, it is returned as is.
    """
    if isinstance(obj, AttributeDict):
        return dict(obj)
    elif isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: complex_handler(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [complex_handler(i) for i in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj


def add_initial_pool_data(cfg: Config, mgr: Any, n_jobs: int = -1):
    """
    Adds initial pool data to the manager.

    Parameters
    ----------
    cfg : Config
        The config object.
    mgr : Any
        The manager object.
    n_jobs : int, optional
        The number of jobs to run in parallel, by default -1

    """
    # Add initial pools for each row in the static_pool_data
    start_time = time.time()
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(mgr.add_pool_to_exchange)(row) for row in mgr.pool_data
    )
    cfg.logger.info(f"Time taken to add initial pools: {time.time() - start_time}")


class CSVReadError(Exception):
    """Raised when a CSV file cannot be read."""

    pass


def read_csv_file(filepath: str, low_memory: bool = False) -> pd.DataFrame:
    """Helper function to read a CSV file.

    Parameters
    ----------
    filepath : str
        The filepath of the CSV file.
    low_memory : bool, optional
        Whether to read the CSV file in low memory mode, by default False

    Returns
    -------
    pd.DataFrame
        The CSV data as a pandas DataFrame.

    Raises
    ------
    CSVReadError
        If the file does not exist or cannot be parsed.
    """
    if not os.path.isfile(filepath):
        raise CSVReadError(f"File {filepath} does not exist")
    try:
        return pd.read_csv(filepath, low_memory=low_memory)
    except pd.errors.ParserError as e:
        raise CSVReadError(f"Error parsing the CSV file {filepath}") from e


def filter_static_pool_data(
    pool_data: pd.DataFrame, exchanges: List[str], sample_size: int or str
) -> pd.DataFrame:
    """Helper function to filter static pool data.

    Parameters
    ----------
    pool_data : pd.DataFrame
        The pool data.
    exchanges : List[str]
        A list of exchanges to fetch data for.
    sample_size : int or str
        The number of Bancor v3 pools to fetch.

    Returns
    -------
    pd.DataFrame
        The filtered pool data.
    """
    filtered_data = pool_data[pool_data["exchange_name"].isin(exchanges)]

    if sample_size != "max":
        bancor_data = filtered_data[filtered_data["exchange_name"] == "bancor_v3"]
        non_bancor_data = filtered_data[
            filtered_data["exchange_name"] != "bancor_v3"
        ].sample(n=sample_size)
        filtered_data = pd.concat([bancor_data, non_bancor_data])

    return filtered_data


def get_static_data(
    cfg: Config,
    exchanges: List[str],
    static_pool_data_filename: str,
    static_pool_data_sample_sz: int or str,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    """
    Helper function to get static pool data, tokens, and Uniswap v2 event mappings.

    Parameters
    ----------
    cfg : Config
        The config object.
    exchanges : List[str]
        A list of exchanges to fetch data for.
    static_pool_data_filename : str
        The filename of the static pool data CSV file.
    static_pool_data_sample_sz : int or str
        The number of Bancor v3 pools to fetch.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]
        A tuple of static pool data, tokens, and Uniswap v2 event mappings.

    """
    base_path = "fastlane_bot/data"

    # Read static pool data from CSV
    static_pool_data_filepath = os.path.join(
        base_path, f"{static_pool_data_filename}.csv"
    )
    static_pool_data = read_csv_file(static_pool_data_filepath)
    static_pool_data = filter_static_pool_data(
        static_pool_data, exchanges, static_pool_data_sample_sz
    )

    # Read Uniswap v2 event mappings and tokens
    uniswap_v2_filepath = os.path.join(base_path, "uniswap_v2_event_mappings.csv")
    uniswap_v2_event_mappings_df = read_csv_file(uniswap_v2_filepath)
    uniswap_v2_event_mappings = dict(
        uniswap_v2_event_mappings_df[["address", "exchange"]].values
    )

    tokens_filepath = os.path.join(base_path, "tokens.csv")
    tokens = read_csv_file(tokens_filepath)

    # Initialize web3
    static_pool_data["cid"] = [
        cfg.w3.keccak(text=f"{row['descr']}").hex()
        for index, row in static_pool_data.iterrows()
    ]

    return static_pool_data, tokens, uniswap_v2_event_mappings


def handle_exchanges(cfg: Config, exchanges: str) -> List[str]:
    """
    Handles the exchanges parameter.

    Parameters
    ----------
    cfg : Config
        The config object.
    exchanges : str
        A comma-separated string of exchanges to fetch data for.

    Returns
    -------
    List[str]
        A list of exchanges to fetch data for.

    """
    # Set external exchanges
    exchanges = exchanges.split(",")
    cfg.logger.info(f"Running data fetching for exchanges: {exchanges}")
    return exchanges


def handle_target_tokens(
    cfg: Config, flashloan_tokens: List[str], target_tokens: str
) -> List[str]:
    """
    Handles the target tokens parameter.

    Parameters
    ----------
    cfg : Config
        The config object.
    flashloan_tokens : List[str]
        A list of flashloan tokens.
    target_tokens : str
        A comma-separated string of target tokens to fetch data for.

    Returns
    -------
    List[str]
        A list of target tokens to fetch data for.

    """
    if target_tokens:
        if target_tokens == "flashloan_tokens":
            target_tokens = flashloan_tokens
        else:
            target_tokens = target_tokens.split(",")
            target_tokens = [
                QueryInterface.cleanup_token_key(token) for token in target_tokens
            ]

            # Ensure that the target tokens are a subset of the flashloan tokens
            for token in flashloan_tokens:
                if token not in target_tokens:
                    cfg.logger.warning(
                        f"Falshloan token {token} not in target tokens. Adding it to target tokens."
                    )
                    target_tokens.append(token)

        cfg.logger.info(
            f"Target tokens are set as: {target_tokens}, {type(target_tokens)}"
        )
    return target_tokens


def handle_flashloan_tokens(cfg: Config, flashloan_tokens: str) -> List[str]:
    """
    Handles the flashloan tokens parameter.

    Parameters
    ----------
    cfg : Config
        The config object.
    flashloan_tokens : str
        A comma-separated string of flashloan tokens to fetch data for.

    Returns
    -------
    List[str]
        A list of flashloan tokens to fetch data for.
    """
    flashloan_tokens = flashloan_tokens.split(",")
    flashloan_tokens = [
        QueryInterface.cleanup_token_key(token) for token in flashloan_tokens
    ]
    # Log the flashloan tokens
    cfg.logger.info(
        f"Flashloan tokens are set as: {flashloan_tokens}, {type(flashloan_tokens)}"
    )
    return flashloan_tokens


def get_config(
    config: str,
    default_min_profit_bnt: int or Decimal,
    limit_bancor3_flashloan_tokens: bool,
    loglevel: str,
) -> Config:
    """
    Gets the config object.

    Parameters
    ----------
    config : str
        The config object.
    default_min_profit_bnt : int or Decimal
        The default minimum profit in BNT.
    limit_bancor3_flashloan_tokens : bool
        Whether to limit the flashloan tokens to Bancor v3 pools.
    loglevel : str
        The log level.

    Returns
    -------
    Config
        The config object.

    """
    default_min_profit_bnt = Decimal(str(default_min_profit_bnt))

    if config and config == "tenderly":
        cfg = Config.new(config=Config.CONFIG_TENDERLY, loglevel=loglevel)
        cfg.logger.info("Using Tenderly config")
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET, loglevel=loglevel)
        cfg.logger.info("Using mainnet config")
    cfg.LIMIT_BANCOR3_FLASHLOAN_TOKENS = limit_bancor3_flashloan_tokens
    cfg.DEFAULT_MIN_PROFIT_BNT = Decimal(str(default_min_profit_bnt))
    cfg.DEFAULT_MIN_PROFIT = Decimal(str(default_min_profit_bnt))
    return cfg


def get_loglevel(loglevel: str) -> Any:
    """
    Gets the log level.

    Parameters
    ----------
    loglevel : str
        The log level.

    Returns
    -------
    Any
        The log level.

    """
    return (
        Config.LOGLEVEL_DEBUG
        if loglevel == "DEBUG"
        else Config.LOGLEVEL_INFO
        if loglevel == "INFO"
        else Config.LOGLEVEL_WARNING
        if loglevel == "WARNING"
        else Config.LOGLEVEL_ERROR
        if loglevel == "ERROR"
        else Config.LOGLEVEL_INFO
    )


def get_event_filters(
    n_jobs: int, mgr: Any, start_block: int, current_block: int, reorg_delay: int
) -> Any:
    """
    Creates event filters for the specified block range.

    Parameters
    ----------
    n_jobs : int
        The number of jobs to run in parallel.
    mgr : Any
        The manager object.
    start_block : int
        The starting block number of the event filters.
    current_block : int
        The current block number of the event filters.
    reorg_delay : int
        The reorg delay.

    Returns
    -------
    Any
        A list of event filters.
    """
    if reorg_delay == 0:
        current_block = "latest"

    return Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(event.createFilter)(fromBlock=start_block, toBlock=current_block)
        for event in mgr.events
    )


def get_all_events(n_jobs: int, event_filters: Any) -> List[Any]:
    """
    Fetches all events using the given event filters.

    Parameters
    ----------
    n_jobs : int
        The number of jobs to run in parallel.
    event_filters : Any
        A list of event filters.

    Returns
    -------
    List[Any]
        A list of all events.
    """
    return Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(event_filter.get_all_entries)() for event_filter in event_filters
    )


def save_events_to_json(
    cache_latest_only,
    logging_path,
    mgr,
    latest_events: List[Any],
    start_block: int,
    current_block: int,
) -> None:
    """
    Saves the given events to a JSON file.

    Parameters
    ----------
    cache_latest_only : bool
        Whether to cache the latest events only.
    logging_path : str
        The logging path.
    mgr : Any
        The manager object.
    latest_events : List[Any]
        A list of the latest events.
    start_block : int
        The starting block number.
    current_block : int
        The current block number.
    """
    if cache_latest_only:
        path = f"{logging_path}latest_event_data.json"
    else:
        if not os.path.isdir("event_data"):
            os.mkdir("event_data")
        path = (
            f"event_data/{mgr.SUPPORTED_EXCHANGES}_{start_block}_{current_block}.json"
        )
    try:
        with open(path, "w") as f:
            latest_events = [
                _["args"].pop("contextId", None) for _ in latest_events
            ] and latest_events
            f.write(json.dumps(latest_events))
    except Exception as e:
        mgr.cfg.logger.error(f"Error saving events to JSON: {e}")

    mgr.cfg.logger.info(f"Saved events to {path}")


def update_pools_from_events(n_jobs: int, mgr: Any, latest_events: List[Any]):
    """
    Updates the pools with the given events.

    Parameters
    ----------
    n_jobs : int
        The number of jobs to run in parallel.
    mgr : Any
        The manager object.

    """
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(mgr.update)(event=event) for event in latest_events
    )


def write_pool_data_to_disk(
    cache_latest_only: bool, logging_path: str, mgr: Any, current_block: int
) -> None:
    """
    Writes the pool data to disk.

    Parameters
    ----------
    cache_latest_only : bool
        Whether to cache the latest pool data only.
    logging_path : str
        The logging path.
    mgr : Any
        The manager object.
    current_block : int
        The current block number.
    """
    if cache_latest_only:
        path = f"{logging_path}latest_pool_data.json"
    else:
        if not os.path.isdir("pool_data"):
            os.mkdir("pool_data")
        path = f"pool_data/{mgr.SUPPORTED_EXCHANGES}_{current_block}.json"
    try:
        with open(path, "w") as f:
            f.write(json.dumps(mgr.pool_data))
    except Exception as e:
        mgr.cfg.logger.error(f"Error writing pool data to disk: {e}")


def parse_bancor3_rows_to_update(
    mgr: Any,
    rows_to_update: List[Hashable],
) -> Tuple[List[Hashable], List[Hashable]]:
    """
    Parses the rows to update for Bancor v3 pools.

    Parameters
    ----------
    mgr : Any
        The manager object.
    rows_to_update : List[Hashable]
        A list of rows to update.

    Returns
    -------
    Tuple[List[Hashable], List[Hashable]]
        A tuple of the Bancor v3 pool rows to update and other pool rows to update.
    """
    bancor3_pool_rows = [
        idx
        for idx in rows_to_update
        if mgr.pool_data[idx]["exchange_name"] == "bancor_v3"
    ]
    other_pool_rows = [
        idx
        for idx in rows_to_update
        if mgr.pool_data[idx]["exchange_name"] != "bancor_v3"
    ]
    return bancor3_pool_rows, other_pool_rows


def init_bot(mgr: Any) -> CarbonBot:
    """
    Initializes the bot.

    Parameters
    ----------
    mgr : Base
        The manager object.

    Returns
    -------
    CarbonBot
        The bot object.
    """
    mgr.cfg.logger.info("Initializing the bot...")
    db = QueryInterface(
        mgr=mgr,
        ConfigObj=mgr.cfg,
        state=mgr.pool_data,
        uniswap_v2_event_mappings=mgr.uniswap_v2_event_mappings,
        exchanges=mgr.exchanges,
    )
    bot = CarbonBot(ConfigObj=mgr.cfg)
    bot.db = db
    assert isinstance(
        bot.db, QueryInterface
    ), "QueryInterface not initialized correctly"
    return bot


def update_pools_from_contracts(
    mgr: Any,
    n_jobs: int,
    rows_to_update: List[int],
    not_bancor_v3: bool = True,
    current_block: int = None,
) -> None:
    """
    Updates the pools with the given indices by calling the contracts.

    Parameters
    ----------
    mgr : Any
        The manager object.
    n_jobs : int
        The number of jobs to run in parallel.
    rows_to_update : List[int]
        A list of rows to update.
    not_bancor_v3 : bool, optional
        Whether the pools are not Bancor v3 pools, by default True
    current_block : int, optional
        The current block number, by default None

    """
    if not_bancor_v3:
        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(mgr.update)(
                pool_info=mgr.pool_data[idx],
                limiter=not_bancor_v3,
                block_number=current_block,
            )
            for idx in rows_to_update
        )
    else:
        with mgr.multicall(address=mgr.cfg.MULTICALL_CONTRACT_ADDRESS):
            for idx, pool in enumerate(rows_to_update):
                mgr.update(
                    pool_info=mgr.pool_data[idx],
                    limiter=not_bancor_v3,
                    block_number=current_block,
                )


def get_cached_events(mgr: Any, logging_path: str) -> List[Any]:
    """
    Gets the cached events.

    Parameters
    ----------
    mgr : Any
        The manager object.
    logging_path : str
        The logging path.

    Returns
    -------
    List[Any]
        A list of the cached events.

    """
    # read data from the json file latest_event_data.json
    mgr.cfg.logger.info("Using cached events")
    path = f"{logging_path}latest_event_data.json"
    os.path.isfile(path)
    with open(path, "r") as f:
        latest_events = json.load(f)
    if not latest_events or len(latest_events) == 0:
        raise ValueError("No events found in the json file")
    mgr.cfg.logger.info(f"Found {len(latest_events)} new events")
    return latest_events


def handle_subsequent_iterations(
    arb_mode: str,
    bot: CarbonBot,
    flashloan_tokens: List[str],
    polling_interval: int,
    randomizer: int,
    run_data_validator: bool,
    target_tokens: List[str] = None,
    loop_idx: int = 0,
):
    """
    Handles the subsequent iterations of the bot.

    Parameters
    ----------
    arb_mode : str
        The arb mode.
    bot : CarbonBot
        The bot object.
    flashloan_tokens : List[str]
        A list of flashloan tokens.
    polling_interval : int
        The polling interval.
    randomizer : int
        The randomizer.
    run_data_validator : bool
        Whether to run the data validator.
    target_tokens : List[str], optional
        A list of target tokens, by default None
    loop_idx : int, optional
        The loop index, by default 0

    """
    if loop_idx > 0:
        bot.db.handle_token_key_cleanup()
        bot.db.remove_unmapped_uniswap_v2_pools()
        bot.db.remove_zero_liquidity_pools()
        bot.db.remove_unsupported_exchanges()

        # Filter the target tokens
        if target_tokens:
            bot.db.filter_target_tokens(target_tokens)

        # Run the bot
        bot.run(
            polling_interval=polling_interval,
            flashloan_tokens=flashloan_tokens,
            mode="single",
            arb_mode=arb_mode,
            run_data_validator=run_data_validator,
            randomizer=randomizer,
        )


def verify_state_changed(bot: CarbonBot, initial_state: List[Dict[str, Any]], mgr: Any):
    """
    Verifies that the state has changed.

    Parameters
    ----------
    bot : CarbonBot
        The bot object.
    initial_state : Dict[str, Any]
        The initial state.
    mgr : Any
        The manager object.

    """
    # Compare the initial state to the final state, and update the state if it has changed
    final_state = mgr.pool_data.copy()
    assert bot.db.state == final_state, "\n *** bot failed to update state *** \n"
    if initial_state != final_state:
        mgr.cfg.logger.info("State has changed...")


def handle_duplicates(mgr: Any):
    """
    Handles the duplicates in the pool data.

    Parameters
    ----------
    mgr : Any
        The manager object.

    """
    # check if any duplicate cid's exist in the pool data
    mgr.deduplicate_pool_data()
    cids = [pool["cid"] for pool in mgr.pool_data]
    assert len(cids) == len(set(cids)), "duplicate cid's exist in the pool data"


def handle_initial_iteration(
    backdate_pools: bool,
    current_block: int,
    last_block: int,
    mgr: Any,
    n_jobs: int,
    start_block: int,
):
    """
    Handles the initial iteration of the bot.

    Parameters
    ----------
    backdate_pools : bool
        Whether to backdate the pools.
    current_block : int
        The current block number.
    last_block : int
        The last block number.
    mgr : Any
        The manager object.
    n_jobs : int
        The number of jobs to run in parallel.
    start_block : int
        The starting block number.

    """
    if last_block == 0:
        mgr.get_rows_to_update(start_block)

        # Construct rows_to_update for "bancor_v3"
        bancor_v3_rows = [
            idx
            for idx, pool in enumerate(mgr.pool_data)
            if pool["exchange_name"] == "bancor_v3"
        ]

        if backdate_pools:
            rows_to_update = bancor_v3_rows

            # Remove duplicates
            rows_to_update = list(set(rows_to_update))

            # Parse the rows to update
            bancor3_pool_rows, other_pool_rows = parse_bancor3_rows_to_update(
                mgr, rows_to_update
            )

            for rows in [bancor3_pool_rows, other_pool_rows]:
                update_pools_from_contracts(
                    mgr,
                    n_jobs=n_jobs,
                    rows_to_update=rows,
                    current_block=current_block,
                )

        elif "bancor_v3" in mgr.exchanges:
            update_pools_from_contracts(
                mgr,
                n_jobs=n_jobs,
                rows_to_update=bancor_v3_rows,
                not_bancor_v3=False,
                current_block=current_block,
            )


def get_latest_events(
    current_block: int,
    mgr: Any,
    n_jobs: int,
    reorg_delay: int,
    start_block: int,
    cache_latest_only: bool,
    logging_path: str,
) -> List[Any]:
    """
    Gets the latest events.

    Parameters
    ----------
    current_block : int
        The current block number.
    mgr : Any
        The manager object.
    n_jobs : int
        The number of jobs to run in parallel.
    reorg_delay : int
        The reorg delay.
    start_block : int
        The starting block number.
    cache_latest_only : bool
        Whether to cache the latest events only.
    logging_path : str
        The logging path.

    Returns
    -------
    List[Any]
        A list of the latest events.
    """
    # Get all event filters, events, and flatten them
    events = [
        complex_handler(event)
        for event in [
            complex_handler(event)
            for event in get_all_events(
                n_jobs,
                get_event_filters(n_jobs, mgr, start_block, current_block, reorg_delay),
            )
        ]
    ]
    # Filter out the latest events per pool, save them to disk, and update the pools
    latest_events = filter_latest_events(mgr, events)
    mgr.cfg.logger.info(f"Found {len(latest_events)} new events")

    # Save the latest events to disk
    save_events_to_json(
        cache_latest_only,
        logging_path,
        mgr,
        latest_events,
        start_block,
        current_block,
    )
    return latest_events


def get_start_block(
    alchemy_max_block_fetch: int, last_block: int, mgr: Any, reorg_delay: int
) -> int:
    """
    Gets the starting block number.

    Parameters
    ----------
    alchemy_max_block_fetch : int
        The maximum number of blocks to fetch.
    last_block : int
        The last block number.
    mgr : Any
        The manager object.
    reorg_delay : int
        The reorg delay.

    Returns
    -------
    int
        The starting block number.

    """
    return (
        max(block["last_updated_block"] for block in mgr.pool_data) - reorg_delay
        if last_block != 0
        else mgr.web3.eth.blockNumber - reorg_delay - alchemy_max_block_fetch
    )


def verify_min_bnt_is_respected(bot: CarbonBot, mgr: Any):
    """
    Verifies that the bot respects the min profit. Used for testing.

    Parameters
    ----------
    bot : CarbonBot
        The bot object.
    mgr : Any
        The manager object.

    """
    # Verify MIN_PROFIT_BNT is set and respected
    assert (
        bot.ConfigObj.DEFAULT_MIN_PROFIT == mgr.cfg.DEFAULT_MIN_PROFIT
    ), "bot failed to update min profit"
    mgr.cfg.logger.debug("Bot successfully updated min profit")
