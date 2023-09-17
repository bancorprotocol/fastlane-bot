# coding=utf-8
"""
Contains the utils functions for events

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import contextlib
import importlib
import json
import os
import sys
import time
from _decimal import Decimal
from typing import Any, Union, Dict, Set, Tuple, Hashable
from typing import List

import brownie
import pandas as pd
import requests
from hexbytes import HexBytes
from joblib import Parallel, delayed
from web3 import Web3
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
    cfg: Config,
    flashloan_tokens: List[str],
    target_tokens: str,
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
    default_min_profit_bnt: int or Decimal,
    limit_bancor3_flashloan_tokens: bool,
    loglevel: str,
    logging_path: str,
    tenderly_fork_id: str = None,
) -> Config:
    """
    Gets the config object.

    Parameters
    ----------
    default_min_profit_bnt : int or Decimal
        The default minimum profit in BNT.
    limit_bancor3_flashloan_tokens : bool
        Whether to limit the flashloan tokens to Bancor v3 pools.
    loglevel : str
        The log level.
    logging_path : str
        The logging path.
    tenderly_fork_id : str, optional
        The Tenderly fork ID, by default None

    Returns
    -------
    Config
        The config object.

    """
    default_min_profit_bnt = Decimal(str(default_min_profit_bnt))

    if tenderly_fork_id:
        cfg = Config.new(
            config=Config.CONFIG_TENDERLY, loglevel=loglevel, logging_path=logging_path
        )
        cfg.logger.info("Using Tenderly config")
    else:
        cfg = Config.new(
            config=Config.CONFIG_MAINNET, loglevel=loglevel, logging_path=logging_path
        )
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
    n_jobs: int, mgr: Any, start_block: int, current_block: int
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

    Returns
    -------
    Any
        A list of event filters.
    """
    bancor_pol_events = ["TradingEnabled", "TokenTraded"]
    by_block_events = Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(event.createFilter)(fromBlock=start_block, toBlock=current_block)
        for event in mgr.events
        if event.__name__ not in bancor_pol_events
    )
    max_num_events = Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(event.createFilter)(fromBlock=0)
        for event in mgr.events
        if event.__name__ in bancor_pol_events
    )
    return by_block_events + max_num_events


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
        path = f"{logging_path}/latest_event_data.json"
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
        path = f"{logging_path}/latest_pool_data.json"
    else:
        if not os.path.isdir("pool_data"):
            os.mkdir("pool_data")
        path = f"pool_data/{mgr.SUPPORTED_EXCHANGES}_{current_block}.json"
    try:
        with open(path, "w") as f:
            f.write(json.dumps(mgr.pool_data))
    except Exception as e:
        mgr.cfg.logger.error(f"Error writing pool data to disk: {e}")


def parse_non_multicall_rows_to_update(
    mgr: Any,
    rows_to_update: List[Hashable],
) -> List[Hashable]:
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

    other_pool_rows = [
        idx
        for idx in rows_to_update
        if mgr.pool_data[idx]["exchange_name"] not in mgr.cfg.MULTICALLABLE_EXCHANGES
    ]
    return other_pool_rows


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
    # bot.TxSubmitHandler.ConfigObj = mgr.cfg
    # bot.TxSubmitHandler.ConfigObj.w3 = mgr.cfg.w3
    # bot.TxSubmitHandler.ConfigObj.w3 = mgr.cfg.w3
    assert isinstance(
        bot.db, QueryInterface
    ), "QueryInterface not initialized correctly"
    return bot


def update_pools_from_contracts(
    mgr: Any,
    n_jobs: int,
    rows_to_update: List[int],
    not_multicall: bool = True,
    token_address: bool = False,
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
    not_multicall : bool, optional
        Whether the pools are not Bancor v3 pools, by default True
    token_address : bool, optional
        Whether to update the token address, by default False
    current_block : int, optional
        The current block number, by default None

    """
    if not_multicall:
        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(mgr.update)(
                pool_info=mgr.pool_data[idx],
                limiter=not_multicall,
                block_number=current_block,
                token_address=token_address,
            )
            for idx in rows_to_update
        )
    else:
        with mgr.multicall(address=mgr.cfg.MULTICALL_CONTRACT_ADDRESS):
            for idx in rows_to_update:
                mgr.update(
                    pool_info=mgr.pool_data[idx],
                    limiter=not_multicall,
                    block_number=current_block,
                    token_address=token_address,
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
    path = "fastlane_bot/data/latest_event_data.json".replace("./logs", "logs")
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
    logging_path: str = None,
    replay_from_block: int = None,
    tenderly_uri: str = None,
    forks_to_cleanup: List[str] = None,
    mgr: Any = None,
    forked_from_block: int = None,
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
    logging_path : str, optional
        The logging path, by default None
    replay_from_block : int, optional
        The block number to replay from, by default None
    tenderly_uri : str, optional
        The Tenderly URI, by default None
    forks_to_cleanup : List[str], optional
        A list of forks to cleanup, by default None
    mgr : Any
        The manager object.
    forked_from_block : int
        The block number to fork from.
    limit_pairs_for_replay : List[str], optional
        A list of pairs to limit replay to, by default None

    """
    if loop_idx > 0 or replay_from_block:
        bot.db.handle_token_key_cleanup()
        bot.db.remove_unmapped_uniswap_v2_pools()
        bot.db.remove_zero_liquidity_pools()
        bot.db.remove_unsupported_exchanges()

        # Filter the target tokens
        if target_tokens:
            bot.db.filter_target_tokens(target_tokens)

        # Log the forked_from_block
        if forked_from_block:
            mgr.cfg.logger.info(
                f"Submitting bot.run with forked_from_block: {forked_from_block}"
            )

        # Run the bot
        bot.run(
            polling_interval=polling_interval,
            flashloan_tokens=flashloan_tokens,
            mode="single",
            arb_mode=arb_mode,
            run_data_validator=run_data_validator,
            randomizer=randomizer,
            logging_path=logging_path,
            replay_mode=True if replay_from_block else False,
            tenderly_fork=tenderly_uri.split("/")[-1] if tenderly_uri else None,
            replay_from_block=forked_from_block,
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
    final_state_bancor_pol = [
        final_state[i]
        for i in range(len(final_state))
        if final_state[i]["exchange_name"] == mgr.cfg.BANCOR_POL_NAME
    ]
    # assert bot.db.state == final_state, "\n *** bot failed to update state *** \n"
    if initial_state != final_state_bancor_pol:
        mgr.cfg.logger.info("State has changed...")
    else:
        mgr.cfg.logger.info("State has not changed...")


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


def get_pools_for_exchange(exchange: str, mgr: Any) -> [Any]:
    """
    Handles the initial iteration of the bot.

    Parameters
    ----------
    mgr : Any
        The manager object.
    exchange : str
        The exchange for which to get pools

    Returns
    -------
    List[Any]
        A list of pools for the specified exchange.
    """
    return [
        idx
        for idx, pool in enumerate(mgr.pool_data)
        if pool["exchange_name"] == exchange
    ]


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
        non_multicall_rows_to_update = mgr.get_rows_to_update(start_block)

        if backdate_pools:
            # Remove duplicates
            non_multicall_rows_to_update = list(set(non_multicall_rows_to_update))

            # Parse the rows to update
            other_pool_rows = parse_non_multicall_rows_to_update(
                mgr, non_multicall_rows_to_update
            )

            for rows in [other_pool_rows]:
                update_pools_from_contracts(
                    mgr,
                    n_jobs=n_jobs,
                    rows_to_update=rows,
                    current_block=current_block,
                )

        # TODO THIS NEEDS TO BE UNCOMMENTED FOR MAINNET
        # if mgr.cfg.BANCOR_POL_NAME in mgr.exchanges:
        #     update_pools_from_contracts(
        #         mgr,
        #         n_jobs=n_jobs,
        #         rows_to_update=[i for i, pool_info in enumerate(mgr.pool_data) if pool_info["exchange_name"] == mgr.cfg.BANCOR_POL_NAME],
        #         current_block=current_block,
        #         token_address=True
        #     )


def multicall_every_iteration(
    current_block: int,
    mgr: Any,
    n_jobs: int,
):
    """
    Handles the initial iteration of the bot.

    Parameters
    ----------
    current_block : int
        The current block number.
    mgr : Any
        The manager object.
    n_jobs : int
        The number of jobs to run in parallel.

    """
    multicallable_pool_rows = [
        list(set(get_pools_for_exchange(mgr=mgr, exchange=ex_name)))
        for ex_name in mgr.cfg.MULTICALLABLE_EXCHANGES
        if ex_name in mgr.exchanges
    ]

    for idx, exchange in enumerate(mgr.cfg.MULTICALLABLE_EXCHANGES):
        update_pools_from_contracts(
            n_jobs=n_jobs,
            current_block=current_block,
            mgr=mgr,
            rows_to_update=multicallable_pool_rows[idx],
            not_multicall=False,
        )


def get_tenderly_pol_events(
    mgr,
    start_block,
    current_block,
    tenderly_fork_id,
):
    """
    Gets the Tenderly POL events.

    Parameters
    ----------
    mgr: Any
        The manager object.
    start_block: int
        The starting block number.
    current_block: int
        The current block number.
    tenderly_fork_id: str
        The Tenderly fork ID.

    Returns
    -------
    List[Any]
        A list of Tenderly POL events.

    """
    # connect to the Tenderly fork
    mgr.cfg.logger.info(
        f"Connecting to Tenderly fork: {tenderly_fork_id}, current_block: {current_block}, start_block: {start_block}"
    )
    contract = mgr.tenderly_event_contracts["bancor_pol"]

    tenderly_events = [
        event.getLogs(fromBlock=current_block - 1000, toBlock=current_block)
        for event in [contract.events.TokenTraded, contract.events.TradingEnabled]
    ]
    tenderly_events = [event for event in tenderly_events if len(event) > 0]
    tenderly_events = [
        complex_handler(event)
        for event in [complex_handler(event) for event in tenderly_events]
    ]
    return tenderly_events


def get_latest_events(
    current_block: int,
    mgr: Any,
    n_jobs: int,
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
    carbon_pol_events = []

    if mgr.tenderly_fork_id:
        carbon_pol_events = get_tenderly_pol_events(
            mgr=mgr,
            start_block=start_block,
            current_block=current_block,
            tenderly_fork_id=mgr.tenderly_fork_id,
        )
        mgr.cfg.logger.info(f"carbon_pol_events: {len(carbon_pol_events)}")

    # Get all event filters, events, and flatten them
    events = [
        complex_handler(event)
        for event in [
            complex_handler(event)
            for event in get_all_events(
                n_jobs,
                get_event_filters(n_jobs, mgr, start_block, current_block),
            )
        ]
    ]

    events += carbon_pol_events

    # Filter out the latest events per pool, save them to disk, and update the pools
    latest_events = filter_latest_events(mgr, events)
    carbon_pol_events = [event for event in latest_events if "token" in event["args"]]
    mgr.cfg.logger.info(
        f"Found {len(latest_events)} new events, {len(carbon_pol_events)} carbon_pol_events"
    )

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
    alchemy_max_block_fetch: int,
    last_block: int,
    mgr: Any,
    reorg_delay: int,
    replay_from_block: int,
) -> Tuple[int, int]:
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
    replay_from_block : int
        The block number to replay from.

    Returns
    -------
    int
        The starting block number.

    """
    if replay_from_block:
        return (
            replay_from_block - 1
            if last_block != 0
            else replay_from_block - reorg_delay - alchemy_max_block_fetch
        ), replay_from_block
    elif mgr.tenderly_fork_id:
        # connect to the Tenderly fork and get the latest block number
        from_block = mgr.w3_tenderly.eth.blockNumber
        return (
            max(block["last_updated_block"] for block in mgr.pool_data) - reorg_delay
            if last_block != 0
            else from_block - reorg_delay - alchemy_max_block_fetch
        ), from_block
    else:
        current_block = mgr.web3.eth.blockNumber
        return (
            (
                max(block["last_updated_block"] for block in mgr.pool_data)
                - reorg_delay
                if last_block != 0
                else current_block - reorg_delay - alchemy_max_block_fetch
            ),
            current_block,
        )


def get_tenderly_block_number(tenderly_fork_id: str) -> int:
    """
    Gets the Tenderly block number.

    Parameters
    ----------
    tenderly_fork_id : str
        The Tenderly fork ID.

    Returns
    -------
    int
        The Tenderly block number.

    """
    provider = Web3.HTTPProvider(f"https://rpc.tenderly.co/fork/{tenderly_fork_id}")
    web3 = Web3(provider)
    return web3.eth.blockNumber


def setup_replay_from_block(mgr: Any, block_number: int) -> Tuple[str, int]:
    """
    Setup a Tenderly fork from a specific block number.

    Parameters
    ----------
    mgr : Any
        The manager object
    block_number: int
        The block number to fork from.

    Returns
    -------
    str
        The web3 provider URL to use for the fork.

    """
    from web3 import Web3

    # The network and block where Tenderly fork gets created
    forkingPoint = {"network_id": "1", "block_number": block_number}

    # Define your Tenderly credentials and project info
    tenderly_access_key = os.getenv("TENDERLY_ACCESS_KEY")
    tenderly_user = os.getenv("TENDERLY_USER")
    tenderly_project = os.getenv("TENDERLY_PROJECT")

    # Base URL for Tenderly's API
    base_url = "https://api.tenderly.co/api/v2"

    # Define the headers for the request
    headers = {"X-Access-Key": tenderly_access_key, "Content-Type": "application/json"}

    # Define the project URL
    project_url = f"account/{tenderly_user}/project/{tenderly_project}"

    # Make the request to create the fork
    fork_response = requests.post(
        f"{base_url}/{project_url}/fork", headers=headers, json=forkingPoint
    )

    # Check if the request was successful
    fork_response.raise_for_status()

    # Parse the JSON response
    fork_data = fork_response.json()

    # Extract the fork id from the response
    fork_id = fork_data["simulation_fork"]["id"]

    def replace_tenderly_fork_id(file_path, fork_id):
        # Read the file content
        with open(file_path, "r") as f:
            content = f.readlines()

        # Perform replacement operation
        replaced = False
        for i, line in enumerate(content):
            if line.startswith("TENDERLY_FORK_ID="):
                content[i] = f"TENDERLY_FORK_ID={fork_id}\n"
                replaced = True
                break

        # If the TENDERLY_FORK_ID was not found, append it
        if not replaced:
            content.append(f"TENDERLY_FORK_ID={fork_id}\n")

        # Write the modified content back to the file
        with open(file_path, "w") as f:
            f.writelines(content)

    # Replace the TENDERLY_FORK_ID in the .env file
    replace_tenderly_fork_id(".env", fork_id)

    # Log the fork id
    mgr.cfg.logger.info(f"Forked with fork id: {fork_id}")

    # Create the provider you can use throughout the rest of your project
    provider = Web3.HTTPProvider(f"https://rpc.tenderly.co/fork/{fork_id}")

    mgr.cfg.logger.info(
        f"Forking from block_number: {block_number}, for fork_id: {fork_id}"
    )

    return provider.endpoint_uri, block_number


def set_network_connection_to_tenderly(
    mgr: Any,
    use_cached_events: bool,
    tenderly_uri: str,
    forked_from_block: int = None,
    tenderly_fork_id: str = None,
) -> Any:
    """
    Set the network connection to Tenderly.

    Parameters
    ----------
    mgr: Any (Manager)
        The manager object.
    use_cached_events: bool
        Whether to use cached events.
    tenderly_uri: str
        The Tenderly URI.
    forked_from_block: int
        The block number the Tenderly fork was created from.
    tenderly_fork_id: str
        The Tenderly fork ID.

    Returns
    -------
    Any (Manager object, Any is used to avoid circular import)
        The manager object.

    """
    assert (
        not use_cached_events
    ), "Cannot replay from block and use cached events at the same time"
    if not tenderly_uri and not tenderly_fork_id:
        tenderly_uri, forked_from_block = setup_replay_from_block(
            mgr, forked_from_block
        )
    elif not tenderly_uri:
        tenderly_uri = f"https://rpc.tenderly.co/fork/{tenderly_fork_id}"
        forked_from_block = None
        mgr.cfg.logger.info(
            f"Using Tenderly fork id: {tenderly_fork_id} at {tenderly_uri}"
        )

    if mgr.cfg.connection.network.is_connected:
        with contextlib.suppress(Exception):
            mgr.cfg.connection.network.disconnect()

    importlib.reload(sys.modules["fastlane_bot.config.connect"])
    from fastlane_bot.config.connect import EthereumNetwork

    connection = EthereumNetwork(
        network_id="tenderly",
        network_name="Tenderly (Alchemy)",
        provider_url=tenderly_uri,
        provider_name="alchemy",
    )
    connection.connect_network()
    mgr.cfg.w3 = connection.web3
    brownie.network.web3.provider.endpoint_uri = tenderly_uri

    if tenderly_fork_id and not forked_from_block:
        forked_from_block = mgr.cfg.w3.eth.blockNumber

    assert (
        mgr.cfg.w3.provider.endpoint_uri == tenderly_uri
    ), f"Failed to connect to Tenderly fork at {tenderly_uri} - got {mgr.cfg.w3.provider.endpoint_uri} instead"
    mgr.cfg.logger.info(f"Successfully connected to Tenderly fork at {tenderly_uri}")
    mgr.cfg.NETWORK = mgr.cfg.NETWORK_TENDERLY
    return mgr, forked_from_block


def set_network_connection_to_mainnet(
    mgr: Any, use_cached_events: bool, mainnet_uri: str
) -> Any:
    """
    Set the network connection to Mainnet.

    Parameters
    ----------
    mgr
    use_cached_events
    mainnet_uri

    Returns
    -------
    Any (Manager object, Any is used to avoid circular import)
        The manager object.

    """

    assert (
        not use_cached_events
    ), "Cannot replay from block and use cached events at the same time"

    if mgr.cfg.connection.network.is_connected:
        with contextlib.suppress(Exception):
            mgr.cfg.connection.network.disconnect()

    importlib.reload(sys.modules["fastlane_bot.config.connect"])
    from fastlane_bot.config.connect import EthereumNetwork

    connection = EthereumNetwork(
        network_id="mainnet",
        network_name="Ethereum Mainnet",
        provider_url=mainnet_uri,
        provider_name="alchemy",
    )
    connection.connect_network()
    mgr.cfg.w3 = connection.web3

    brownie.network.web3.provider.endpoint_uri = mainnet_uri

    assert (
        mgr.cfg.w3.provider.endpoint_uri == mainnet_uri
    ), f"Failed to connect to Mainnet at {mainnet_uri} - got {mgr.cfg.w3.provider.endpoint_uri} instead"
    mgr.cfg.logger.info("Successfully connected to Mainnet")
    mgr.cfg.NETWORK = mgr.cfg.NETWORK_MAINNET
    return mgr


def handle_limit_pairs_for_replay_mode(
    cfg: Config,
    limit_pairs_for_replay: str,
    replay_from_block: int,
    static_pool_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Splits, validates, and logs the `limit_pairs_for_replay` for replay mode.

    Parameters
    ----------
    cfg: Config
        The config object.
    limit_pairs_for_replay: str
        A comma-separated list of pairs to limit replay to. Must be in the format
    replay_from_block: int
        The block number to replay from. (For debugging / testing)
    static_pool_data: pd.DataFrame
        The static pool data.

    Returns
    -------
    pd.DataFrame
        The static pool data.

    """
    if limit_pairs_for_replay and replay_from_block:
        limit_pairs_for_replay = limit_pairs_for_replay.split(",")
        cfg.logger.info(f"Limiting replay to pairs: {limit_pairs_for_replay}")
        static_pool_data = static_pool_data[
            static_pool_data["pair_name"].isin(limit_pairs_for_replay)
        ]
    return static_pool_data


def set_network_to_tenderly_if_replay(
    last_block: int,
    loop_idx: int,
    mgr: Any,
    replay_from_block: int,
    tenderly_uri: str,
    use_cached_events: bool,
    forked_from_block: int = None,
    tenderly_fork_id: str = None,
) -> Tuple[Any, str, Any]:
    """
    Set the network connection to Tenderly if replaying from a block

    Parameters
    ----------
    last_block : int
        The last block that was processed
    loop_idx : int
        The current loop index
    mgr : Any
        The manager object
    replay_from_block : int
        The block to replay from
    tenderly_uri : str
        The Tenderly URI
    use_cached_events : bool
        Whether to use cached events
    forked_from_block : int
        The block number the Tenderly fork was created from.
    tenderly_fork_id : str
        The Tenderly fork id

    Returns
    -------
    mgr : Any
        The manager object
    tenderly_uri : str
        The Tenderly URI
    forked_from_block : int
        The block number the Tenderly fork was created from.
    """
    if not replay_from_block and not tenderly_fork_id:
        return mgr, tenderly_uri, None

    if last_block == 0:
        mgr.cfg.logger.info(f"Setting network connection to Tenderly idx: {loop_idx}")
        mgr, forked_from_block = set_network_connection_to_tenderly(
            mgr=mgr,
            use_cached_events=use_cached_events,
            tenderly_uri=tenderly_uri,
            forked_from_block=forked_from_block,
            tenderly_fork_id=tenderly_fork_id,
        )
        tenderly_uri = mgr.cfg.w3.provider.endpoint_uri
        return mgr, tenderly_uri, forked_from_block

    if replay_from_block and loop_idx > 0 and mgr.cfg.NETWORK != "tenderly":
        # Tx must always be submitted from Tenderly when in replay mode
        mgr.cfg.logger.info(f"Setting network connection to Tenderly idx: {loop_idx}")
        mgr, forked_from_block = set_network_connection_to_tenderly(
            mgr=mgr,
            use_cached_events=use_cached_events,
            tenderly_uri=tenderly_uri,
            forked_from_block=forked_from_block,
        )
        mgr.cfg.w3.provider.endpoint_uri = tenderly_uri
        return mgr, tenderly_uri, forked_from_block

    return mgr, tenderly_uri, forked_from_block


def set_network_to_mainnet_if_replay(
    last_block: int,
    loop_idx: int,
    mainnet_uri: str,
    mgr: Any,
    replay_from_block: int,
    use_cached_events: bool,
):
    """
    Set the network connection to Mainnet if replaying from a block

    Parameters
    ----------
    last_block : int
        The last block that the bot processed
    loop_idx : int
        The current loop index
    mainnet_uri : str
        The URI of the Mainnet node
    mgr : Any
        The manager object
    replay_from_block : int
        The block to replay from
    use_cached_events : bool
        Whether to use cached events

    Returns
    -------
    mgr : Any
        The manager object

    """
    if (
        (replay_from_block or mgr.tenderly_fork_id)
        and mgr.cfg.NETWORK != "mainnet"
        and last_block != 0
    ):
        mgr.cfg.logger.info(f"Setting network connection to Mainnet idx: {loop_idx}")
        mgr = set_network_connection_to_mainnet(
            mgr=mgr,
            use_cached_events=use_cached_events,
            mainnet_uri=mainnet_uri,
        )
    return mgr


def append_fork_for_cleanup(forks_to_cleanup: List[str], tenderly_uri: str):
    """
    Appends the fork to the forks_to_cleanup list if it is not None.

    Parameters
    ----------
    forks_to_cleanup : List[str]
        The list of forks to cleanup.
    tenderly_uri : str
        The tenderly uri.

    Returns
    -------
    forks_to_cleanup : List[str]
        The list of forks to cleanup.

    """
    if tenderly_uri is not None:
        forks_to_cleanup.append(tenderly_uri.split("/")[-1])
    return forks_to_cleanup


def delete_tenderly_forks(forks_to_cleanup: List[str], mgr: Any) -> List[str]:
    """
    Deletes the forks that were created on Tenderly.

    Parameters
    ----------
    forks_to_cleanup : List[str]
        List of Tenderly fork names to delete.
    mgr : Any
        The manager object.
    """

    forks_to_keep = [forks_to_cleanup[-1], forks_to_cleanup[-2]]
    forks_to_cleanup = [fork for fork in forks_to_cleanup if fork not in forks_to_keep]

    # Delete the forks
    for fork in forks_to_cleanup:
        # Define your Tenderly credentials and project info
        tenderly_access_key = os.getenv("TENDERLY_ACCESS_KEY")
        tenderly_project = os.getenv("TENDERLY_PROJECT")

        # Define the headers for the request
        headers = {
            "X-Access-Key": tenderly_access_key,
            "Content-Type": "application/json",
        }

        url = f"https://api.tenderly.co/api/v2/project/{tenderly_project}/forks/{fork}"

        # Make the request to create the fork
        fork_response = requests.delete(url, headers=headers)

        mgr.cfg.logger.info(
            f"Delete Fork {fork}, Response: {fork_response.status_code}"
        )

    return forks_to_keep


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


def handle_target_token_addresses(static_pool_data: pd.DataFrame, target_tokens: List):
    """
    Get the addresses of the target tokens.

    Parameters
    ----------
    static_pool_data : pd.DataFrame
        The static pool data.
    target_tokens : List
        The target tokens.

    Returns
    -------
    List
        The addresses of the target tokens.

    """
    # Get the addresses of the target tokens
    target_token_addresses = []
    if target_tokens:
        for token in target_tokens:
            target_token_addresses = (
                target_token_addresses
                + static_pool_data[static_pool_data["tkn0_key"] == token][
                    "tkn0_address"
                ].tolist()
            )
            target_token_addresses = (
                target_token_addresses
                + static_pool_data[static_pool_data["tkn1_key"] == token][
                    "tkn1_address"
                ].tolist()
            )
    target_token_addresses = list(set(target_token_addresses))
    return target_token_addresses


def handle_replay_from_block(replay_from_block: int) -> (int, int, bool):
    """
    Handle the replay from block flag.

    Parameters
    ----------
    replay_from_block : int
        The block number to replay from.

    Returns
    -------
    polling_interval : int
        The time interval at which the bot polls for new events.

    """
    assert (
        replay_from_block > 0
    ), "The block number to replay from must be greater than 0."
    reorg_delay = 0
    use_cached_events = False
    polling_interval = 0
    return polling_interval, reorg_delay, use_cached_events


#%%
