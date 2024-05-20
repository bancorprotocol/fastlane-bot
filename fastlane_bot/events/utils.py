"""
Contains the utils functions for events

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import base64
import json
import os
import random
import time
from _decimal import Decimal
from glob import glob
from typing import Any, Union, Dict, Set, Tuple, Hashable
from typing import List

import numpy as np
import pandas as pd
import requests
from hexbytes import HexBytes
from joblib import Parallel, delayed
from web3 import AsyncWeb3, Web3
from web3.datastructures import AttributeDict

from fastlane_bot import Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.data.abi import FAST_LANE_CONTRACT_ABI
from fastlane_bot.exceptions import ReadOnlyException
from fastlane_bot.events.interface import QueryInterface

from fastlane_bot.helpers import TxHelpers
from fastlane_bot.utils import safe_int
from .interfaces.event import Event


def filter_latest_events(
    mgr: Any, events: List[Event]
) -> List[Event]:
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

    # Handles the case where multiple pools are created in the same block
    events.reverse()

    bancor_v2_anchor_addresses = {
        pool["anchor"] for pool in mgr.pool_data if pool["exchange_name"] == "bancor_v2"
    }

    for event in events:
        pool_type = mgr.pool_type_from_exchange_name(mgr.exchange_name_from_event(event))
        if pool_type:
            key = pool_type.unique_key()
        else:
            continue
        if key == "cid":
            key = "id"
        elif key == "tkn1_address":
            if event.args["pool"] != mgr.cfg.BNT_ADDRESS:
                key = "pool"
            else:
                key = "tkn_address"

        unique_key = event.address if key == "address" else event.args[key]
        # unique_key = event.args[key]

        # Skip events for Bancor v2 anchors
        if (
            key == "address"
            and "_token1" in event.args
            and (
                event.args["_token1"] in bancor_v2_anchor_addresses
                or event.args["_token2"] in bancor_v2_anchor_addresses
            )
        ):
            continue

        if unique_key in latest_entry_per_pool:
            if event.block_number > latest_entry_per_pool[unique_key].block_number:
                latest_entry_per_pool[unique_key] = event
            elif event.block_number == latest_entry_per_pool[unique_key].block_number:
                if event.transaction_index == latest_entry_per_pool[unique_key].transaction_index:
                    if event.log_index > latest_entry_per_pool[unique_key].log_index:
                        latest_entry_per_pool[unique_key] = event
                elif event.transaction_index > latest_entry_per_pool[unique_key].transaction_index:
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
        return complex_handler(dict(obj))
    elif isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: complex_handler(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [complex_handler(i) for i in obj]
    elif isinstance(obj, set):
        return complex_handler(list(obj))
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
    cfg.logger.debug(
        f"[events.utils] Time taken to add initial pools: {time.time() - start_time}"
    )


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


def get_tkn_symbol(tkn_address, tokens: pd.DataFrame) -> str:
    """
    Gets the token symbol for logging purposes
    :param tkn_address: the token address
    :param tokens: the Dataframe containing token information

    returns: str
    """
    try:
        return tokens.loc[tokens["address"] == tkn_address]["symbol"].values[0]
    except Exception:
        return tkn_address


def get_tkn_symbols(flashloan_tokens, tokens: pd.DataFrame) -> List:
    """
    Gets the token symbol for logging purposes
    :param flashloan_tokens: the flashloan token addresses
    :param tokens: the Dataframe containing token information

    returns: list
    """
    flashloan_tokens = flashloan_tokens.split(",")
    flashloan_tkn_symbols = []
    for tkn in flashloan_tokens:
        flashloan_tkn_symbols.append(get_tkn_symbol(tkn_address=tkn, tokens=tokens))
    return flashloan_tkn_symbols


def get_static_data(
    cfg: Config,
    exchanges: List[str],
    blockchain: str,
    static_pool_data_filename: str,
    read_only: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Helper function to get static pool data, tokens, and Uniswap v2 event mappings.

    Parameters
    ----------
    cfg : Config
        The config object.
    exchanges : List[str]
        A list of exchanges to fetch data for.
    blockchain : str
        The name of the blockchain being used
    static_pool_data_filename : str
        The filename of the static pool data CSV file.
    read_only : bool, optional
        Whether to run the bot in read-only mode, by default False

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]
        A tuple of static pool data, tokens, and Uniswap v2 event mappings.

    """
    base_path = os.path.normpath(f"fastlane_bot/data/blockchain_data/{blockchain}/")
    # Read static pool data from CSV
    static_pool_data_filepath = os.path.join(
        base_path, f"{static_pool_data_filename}.csv"
    )
    static_pool_data = read_csv_file(static_pool_data_filepath)
    static_pool_data = static_pool_data[
        static_pool_data["exchange_name"].isin(exchanges)
    ]

    # Read Uniswap v2 event mappings and tokens
    uniswap_v2_filepath = os.path.join(base_path, "uniswap_v2_event_mappings.csv")
    uniswap_v2_event_mappings_df = read_csv_file(uniswap_v2_filepath)
    uniswap_v2_event_mappings = dict(
        uniswap_v2_event_mappings_df[["address", "exchange"]].values
    )

    # Read Uniswap v3 event mappings and tokens
    uniswap_v3_filepath = os.path.join(base_path, "uniswap_v3_event_mappings.csv")
    uniswap_v3_event_mappings_df = read_csv_file(uniswap_v3_filepath)
    uniswap_v3_event_mappings = dict(
        uniswap_v3_event_mappings_df[["address", "exchange"]].values
    )
    # Read Solidly v2 event mappings and tokens
    solidly_v2_filepath = os.path.join(base_path, "solidly_v2_event_mappings.csv")
    solidly_v2_event_mappings_df = read_csv_file(solidly_v2_filepath)
    solidly_v2_event_mappings = dict(
        solidly_v2_event_mappings_df[["address", "exchange"]].values
    )

    tokens_filepath = os.path.join(base_path, "tokens.csv")
    if not os.path.exists(tokens_filepath) and not read_only:
        df = pd.DataFrame(columns=["address", "symbol", "decimals"])
        df.to_csv(tokens_filepath)
    elif not os.path.exists(tokens_filepath) and read_only:
        raise ReadOnlyException(
            f"Tokens file {tokens_filepath} does not exist. Please run the bot in non-read-only mode to create it."
        )
    tokens = read_csv_file(tokens_filepath)
    tokens["address"] = tokens["address"].apply(lambda x: Web3.to_checksum_address(x))
    tokens = tokens.drop_duplicates(subset=["address"])
    tokens = tokens.dropna(subset=["decimals", "symbol", "address"])
    tokens["symbol"] = (
        tokens["symbol"]
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )

    def correct_tkn(tkn_address, keyname):
        try:
            return tokens[tokens["address"] == tkn_address][keyname].values[0]
        except IndexError:
            return np.nan

    static_pool_data["tkn0_address"] = static_pool_data["tkn0_address"].apply(
        lambda x: Web3.to_checksum_address(x)
    )
    static_pool_data["tkn1_address"] = static_pool_data["tkn1_address"].apply(
        lambda x: Web3.to_checksum_address(x)
    )
    static_pool_data["tkn0_decimals"] = static_pool_data["tkn0_address"].apply(
        lambda x: correct_tkn(x, "decimals")
    )
    static_pool_data["tkn1_decimals"] = static_pool_data["tkn1_address"].apply(
        lambda x: correct_tkn(x, "decimals")
    )

    static_pool_data["tkn0_symbol"] = static_pool_data["tkn0_address"].apply(
        lambda x: correct_tkn(x, "symbol")
    )
    static_pool_data["tkn1_symbol"] = static_pool_data["tkn1_address"].apply(
        lambda x: correct_tkn(x, "symbol")
    )
    static_pool_data["pair_name"] = (
        static_pool_data["tkn0_address"] + "/" + static_pool_data["tkn1_address"]
    )
    static_pool_data = static_pool_data.dropna(
        subset=[
            "pair_name",
            "exchange_name",
            "fee",
            "tkn0_symbol",
            "tkn1_symbol",
            "tkn0_decimals",
            "tkn1_decimals",
        ]
    )

    static_pool_data["descr"] = (
        static_pool_data["exchange_name"]
        + " "
        + static_pool_data["pair_name"]
        + " "
        + static_pool_data["fee"].astype(str)
    )
    # Initialize web3
    static_pool_data["cid"] = [
        cfg.w3.keccak(text=f"{row['descr']}").hex()
        for index, row in static_pool_data.iterrows()
    ]

    static_pool_data = static_pool_data.drop_duplicates(subset=["cid"])
    static_pool_data.reset_index(drop=True, inplace=True)

    return (
        static_pool_data,
        tokens,
        uniswap_v2_event_mappings,
        uniswap_v3_event_mappings,
        solidly_v2_event_mappings,
    )


def handle_tenderly_event_exchanges(
    cfg: Config, exchanges: str, tenderly_fork_id: str
) -> List[str]:
    """
    Handles the exchanges parameter.

    Parameters
    ----------
    cfg : Config
        The config object.
    exchanges : str
        A comma-separated string of exchanges to fetch data for.
    tenderly_fork_id : str
        The Tenderly fork ID.

    Returns
    -------
    List[str]
        A list of exchanges to fetch data for.

    """
    if not tenderly_fork_id:
        return []

    if not exchanges or exchanges == "None":
        return []

    exchanges = exchanges.split(",") if exchanges else []
    cfg.logger.info(
        f"[events.utils] [events.utils.handle_tenderly_event_exchanges] Running data fetching for exchanges: {exchanges}"
    )
    return exchanges


def add_fork_exchanges(cfg: Config, exchanges: List) -> List[str]:

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
    # Check fork settings
    if "uniswap_v2_forks" in exchanges:
        exchanges += cfg.UNI_V2_FORKS
        exchanges.remove("uniswap_v2_forks")
    if "uniswap_v3_forks" in exchanges:
        exchanges += cfg.UNI_V3_FORKS
        exchanges.remove("uniswap_v3_forks")
    if "solidly_v2_forks" in exchanges:
        exchanges += cfg.SOLIDLY_V2_FORKS
        exchanges.remove("solidly_v2_forks")
    if "carbon_v1_forks" in exchanges:
        exchanges += cfg.CARBON_V1_FORKS
        exchanges.remove("carbon_v1_forks")
    exchanges = list(set(exchanges))
    return exchanges


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
    exchanges = exchanges.split(",") if exchanges else []
    exchanges = add_fork_exchanges(cfg=cfg, exchanges=exchanges)
    cfg.logger.info(f"[events.utils] Running data fetching for exchanges: {exchanges}")
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
            # target_tokens = [
            #     QueryInterface.cleanup_token_key(token) for token in target_tokens
            # ]

            # Ensure that the target tokens are a subset of the flashloan tokens
            for token in flashloan_tokens:
                if token not in target_tokens:
                    cfg.logger.warning(
                        f"[events.utils.handle_target_tokens] Flashloan token {token} not in target tokens. Adding it to target tokens."
                    )
                    target_tokens.append(token)

        cfg.logger.info(
            f"[events.utils.handle_target_tokens] Target tokens are set as: {target_tokens}, {type(target_tokens)}"
        )

    return target_tokens


def handle_flashloan_tokens(
    cfg: Config, flashloan_tokens: str, tokens: pd.DataFrame
) -> List[str]:
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
    flt_symbols = get_tkn_symbols(flashloan_tokens=flashloan_tokens, tokens=tokens)
    flashloan_tokens = flashloan_tokens.split(",")
    unique_tokens = len(tokens["address"].unique())
    cfg.logger.info(f"unique_tokens: {unique_tokens}")

    cfg.logger.info(
        f"[events.utils.handle_flashloan_tokens] unique_tokens: {unique_tokens}"
    )
    flashloan_tokens = [
        tkn for tkn in flashloan_tokens if tkn in tokens["address"].unique()
    ]

    # Log the flashloan tokens
    cfg.logger.info(
        f"[events.utils.handle_flashloan_tokens] Flashloan tokens are set as: {flt_symbols}, {type(flashloan_tokens)}"
    )
    return flashloan_tokens


def get_config(
    default_min_profit_gas_token: str,
    limit_bancor3_flashloan_tokens: bool,
    loglevel: str,
    logging_path: str,
    blockchain: str,
    flashloan_tokens: str,
    tenderly_fork_id: str = None,
    self_fund: bool = False,
    rpc_url: str = None,
) -> Config:
    """
    Gets the config object.

    Parameters
    ----------
    default_min_profit_gas_token : int or Decimal
        The default minimum profit in the gas token.
    limit_bancor3_flashloan_tokens : bool
        Whether to limit the flashloan tokens to Bancor v3 pools.
    loglevel : str
        The log level.
    logging_path : str
        The logging path.
    blockchain : str
        The name of the blockchain
    flashloan_tokens (str):
        Comma seperated list of tokens that the bot can use for flash loans.
    tenderly_fork_id : str, optional
        The Tenderly fork ID, by default None
    self_fund : bool
        The bot will default to using flashloans if False, otherwise it will attempt to use funds from the wallet.
    rpc_url : str, optional
        The RPC URL to use, by default None
    Returns
    -------
    Config
        The config object.

    """
    default_min_profit_gas_token = Decimal(default_min_profit_gas_token)

    if tenderly_fork_id:
        cfg = Config.new(
            config=Config.CONFIG_TENDERLY,
            loglevel=loglevel,
            logging_path=logging_path,
            blockchain=blockchain,
            self_fund=self_fund,
        )
        cfg.logger.info("[events.utils.get_config] Using Tenderly config")
    else:
        cfg = Config.new(
            config=Config.CONFIG_MAINNET,
            loglevel=loglevel,
            logging_path=logging_path,
            blockchain=blockchain,
            self_fund=self_fund,
        )
        cfg.logger.info("[events.utils.get_config] Using mainnet config")

    if rpc_url:
        cfg.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 60}))
        cfg.w3_async = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
        if 'tenderly' in rpc_url:
            cfg.NETWORK = cfg.NETWORK_TENDERLY
        cfg.WEB3_ALCHEMY_PROJECT_ID = rpc_url.split("/")[-1]
        cfg.RPC_ENDPOINT = rpc_url.replace(cfg.WEB3_ALCHEMY_PROJECT_ID, "")
        cfg.RPC_URL = rpc_url
        cfg.BANCOR_ARBITRAGE_CONTRACT = cfg.w3.eth.contract(
            address=cfg.w3.to_checksum_address(cfg.network.FASTLANE_CONTRACT_ADDRESS),
            abi=FAST_LANE_CONTRACT_ABI,
        )

    cfg.LIMIT_BANCOR3_FLASHLOAN_TOKENS = limit_bancor3_flashloan_tokens
    cfg.DEFAULT_MIN_PROFIT_GAS_TOKEN = Decimal(default_min_profit_gas_token)
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

    # Get for exchanges except POL contract
    by_block_events = Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(event.create_filter)(fromBlock=start_block, toBlock=current_block)
        for event in mgr.events
        if event.__name__ not in bancor_pol_events
    )

    # Get all events since the beginning of time for Bancor POL contract
    max_num_events = Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(event.create_filter)(fromBlock=0, toBlock="latest")
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

    def throttled_get_all_entries(event_filter):
        try:
            return event_filter.get_all_entries()
        except Exception as e:
            if "Too Many Requests for url" in str(e):
                time.sleep(random.random())
                return event_filter.get_all_entries()
            else:
                raise e

    return Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(throttled_get_all_entries)(event_filter)
        for event_filter in event_filters
    )


def convert_to_serializable(data: Any) -> Any:
    if isinstance(data, bytes):
        return base64.b64encode(data).decode("ascii")
    elif isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif hasattr(data, "__dict__"):
        return convert_to_serializable(data.__dict__)
    else:
        return data


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
            # Remove contextId from the latest events
            latest_events = convert_to_serializable(latest_events)
            # latest_events = [
            #     _["args"].pop("contextId", None) for _ in latest_events
            # ] and latest_events
            f.write(json.dumps(latest_events))
            mgr.cfg.logger.info(f"Saved events to {path}")
    except Exception as e:
        mgr.cfg.logger.warning(
            f"[events.utils.save_events_to_json]: {e}. "
            f"This will not impact bot functionality. "
            f"Skipping..."
        )
    mgr.cfg.logger.debug(f"[events.utils.save_events_to_json] Saved events to {path}")


def process_new_events(new_event_mappings, event_mappings, filename, read_only):
    # Update the manager's event mappings
    event_mappings.update(new_event_mappings)
    
    if not read_only:
        # Update the local event_mappings csvs
        df = pd.DataFrame.from_dict(event_mappings, orient='index').reset_index()
        if len(df)>0:
            df.columns = ['address', 'exchange']
            # if the csvs are always sorted then the diffs will be readable
            df.sort_values(by=['exchange','address'], inplace=True)
            df.to_csv(filename, index=False)


def update_pools_from_events(n_jobs: int, mgr: Any, latest_events: List[Event]):
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
        delayed(mgr.update_from_event)(event=event) for event in latest_events
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
        df = pd.DataFrame(mgr.pool_data)

        def remove_nan(row):
            return {col: val for col, val in row.items() if pd.notna(val)}

        # Apply the function to each row
        cleaned_df = df.apply(remove_nan, axis=1)
        cleaned_df.to_json(path, orient="records")
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
    rows_to_update: List[int] or List[Hashable],
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
    current_block : int, optional
        The current block number, by default None

    """
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(mgr.update)(
            pool_info=mgr.pool_data[idx],
            block_number=current_block,
        )
        for idx in rows_to_update
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
    mgr.cfg.logger.info("[events.utils] Using cached events...")
    path = "fastlane_bot/data/latest_event_data.json".replace("./logs", "logs")
    os.path.isfile(path)
    with open(path, "r") as f:
        latest_events = json.load(f)
    if not latest_events or len(latest_events) == 0:
        raise ValueError("No events found in the json file")
    mgr.cfg.logger.info(f"[events.utils] Found {len(latest_events)} new events")
    return latest_events


def handle_subsequent_iterations(
    arb_mode: str,
    bot: CarbonBot,
    flashloan_tokens: List[str],
    randomizer: int,
    target_tokens: List[str] = None,
    loop_idx: int = 0,
    logging_path: str = None,
    replay_from_block: int = None,
    tenderly_uri: str = None,
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
    randomizer : int
        The randomizer.
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
    mgr : Any
        The manager object.
    forked_from_block : int
        The block number to fork from.

    """
    if loop_idx > 0 or replay_from_block:
        # bot.db.handle_token_key_cleanup()
        bot.db.remove_unmapped_uniswap_v2_pools()
        bot.db.remove_zero_liquidity_pools()
        bot.db.remove_unsupported_exchanges()
        # bot.db.remove_faulty_token_pools()
        # bot.db.remove_pools_with_invalid_tokens()
        # bot.db.ensure_descr_in_pool_data()

        # Filter the target tokens
        if target_tokens:
            bot.db.filter_target_tokens(target_tokens)

        # Log the forked_from_block
        if forked_from_block:
            mgr.cfg.logger.info(
                f"[events.utils] Submitting bot.run with forked_from_block: {forked_from_block}, replay_from_block {replay_from_block}"
            )
            mgr.cfg.w3 = Web3(Web3.HTTPProvider(tenderly_uri))
            bot.db.cfg.w3 = Web3(Web3.HTTPProvider(tenderly_uri))
            bot.ConfigObj.w3 = Web3(Web3.HTTPProvider(tenderly_uri))

        # Run the bot
        bot.run(
            flashloan_tokens=flashloan_tokens,
            arb_mode=arb_mode,
            randomizer=randomizer,
            logging_path=logging_path,
            replay_mode=True if replay_from_block else False,
            replay_from_block=forked_from_block,
        )


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


def get_tenderly_events(
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
    tenderly_events_all = []
    tenderly_exchanges = mgr.tenderly_event_exchanges
    for exchange in tenderly_exchanges:
        contract = mgr.tenderly_event_contracts[exchange]
        exchange_events = mgr.exchanges[exchange].get_events(contract)

        tenderly_events = [
            event.getLogs(fromBlock=current_block - 1000, toBlock=current_block)
            for event in exchange_events
        ]

        tenderly_events = [event for event in tenderly_events if len(event) > 0]
        tenderly_events = [
            complex_handler(event)
            for event in [complex_handler(event) for event in tenderly_events]
        ]
        tenderly_events_all += tenderly_events
    return tenderly_events_all


def get_latest_events(
    current_block: int,
    mgr: Any,
    n_jobs: int,
    start_block: int,
    cache_latest_only: bool,
    logging_path: str,
    event_gatherer: "EventGatherer"
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
    tenderly_events = []

    if mgr.tenderly_fork_id and mgr.tenderly_event_exchanges:
        tenderly_events = get_tenderly_events(
            mgr=mgr,
            start_block=start_block,
            current_block=current_block,
            tenderly_fork_id=mgr.tenderly_fork_id,
        )
        mgr.cfg.logger.info(
            f"[events.utils.get_latest_events] tenderly_events: {len(tenderly_events)}"
        )

    # Get all events
    events = event_gatherer.get_all_events(from_block=start_block, to_block=current_block)

    # Filter out the latest events per pool, save them to disk, and update the pools
    latest_events = filter_latest_events(mgr, events)
    if mgr.tenderly_fork_id:
        if tenderly_events:
            latest_tenderly_events = filter_latest_events(mgr, tenderly_events)
            latest_events += latest_tenderly_events

        # remove the events from any mgr.tenderly_event_exchanges exchanges
        for exchange in mgr.tenderly_event_exchanges:
            if pool_type := mgr.pool_type_from_exchange_name(exchange):
                latest_events = [
                    event
                    for event in latest_events
                    if not pool_type.event_matches_format(event)
                ]

    carbon_pol_events = [event for event in latest_events if "token" in event.args]
    mgr.cfg.logger.info(
        f"[events.utils.get_latest_events] Found {len(latest_events)} new events, {len(carbon_pol_events)} carbon_pol_events"
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
) -> Tuple[int, int or None]:
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
    Tuple[int, int or None]
        The starting block number and the block number to replay from.

    """
    if last_block == 0:
        if replay_from_block:
            return replay_from_block - reorg_delay - alchemy_max_block_fetch, replay_from_block
        elif mgr.tenderly_fork_id:
            return mgr.w3_tenderly.eth.block_number - reorg_delay - alchemy_max_block_fetch, mgr.w3_tenderly.eth.block_number
        else:
            return mgr.web3.eth.block_number - reorg_delay - alchemy_max_block_fetch, None
    else:
        if replay_from_block:
            return replay_from_block - 1, replay_from_block
        elif mgr.tenderly_fork_id:
            return safe_int(max(block["last_updated_block"] for block in mgr.pool_data)) - reorg_delay, mgr.w3_tenderly.eth.block_number
        else:
            return safe_int(max(block["last_updated_block"] for block in mgr.pool_data)) - reorg_delay, None


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
    base_url = "https://api.tenderly.co/api/v1"

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

    # Log the fork id
    mgr.cfg.logger.info(
        f"[events.utils.setup_replay_from_block] Forked with fork id: {fork_id}"
    )

    # Create the provider you can use throughout the rest of your project
    provider = Web3.HTTPProvider(f"https://rpc.tenderly.co/fork/{fork_id}")

    mgr.cfg.logger.info(
        f"[events.utils.setup_replay_from_block] Forking from block_number: {block_number}, for fork_id: {fork_id}"
    )

    return provider.endpoint_uri, block_number


def set_network_connection_to_tenderly(
    mgr: Any,
    use_cached_events: bool,
    tenderly_uri: str,
    forked_from_block: int = None,
    tenderly_fork_id: str = None,
) -> int:
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
    int The block number the Tenderly fork was created from.

    """
    assert (
        not use_cached_events
    ), "Cannot replay from block and use cached events at the same time"
    if not tenderly_uri and not tenderly_fork_id:
        return forked_from_block
    elif tenderly_fork_id:
        tenderly_uri = f"https://rpc.tenderly.co/fork/{tenderly_fork_id}"
        forked_from_block = None
        mgr.cfg.logger.info(
            f"[events.utils.set_network_connection_to_tenderly] Using Tenderly fork id: {tenderly_fork_id} at {tenderly_uri}"
        )
        mgr.cfg.w3 = Web3(Web3.HTTPProvider(tenderly_uri))
    elif tenderly_uri:
        mgr.cfg.logger.info(
            f"[events.utils.set_network_connection_to_tenderly] Connecting to Tenderly fork at {tenderly_uri}"
        )
        mgr.cfg.w3 = Web3(Web3.HTTPProvider(tenderly_uri))

    if tenderly_fork_id and not forked_from_block:
        forked_from_block = mgr.cfg.w3.eth.block_number

    assert (
        mgr.cfg.w3.provider.endpoint_uri == tenderly_uri
    ), f"Failed to connect to Tenderly fork at {tenderly_uri} - got {mgr.cfg.w3.provider.endpoint_uri} instead"
    mgr.cfg.logger.info(
        f"[events.utils.set_network_connection_to_tenderly] Successfully connected to Tenderly fork at {tenderly_uri}, forked from block: {forked_from_block}"
    )
    mgr.cfg.NETWORK = mgr.cfg.NETWORK_TENDERLY
    return forked_from_block


def set_network_connection_to_mainnet(
    mgr: Any, use_cached_events: bool, mainnet_uri: str
):
    """
    Set the network connection to Mainnet.

    Parameters
    ----------
    mgr
    use_cached_events
    mainnet_uri

    """

    assert (
        not use_cached_events
    ), "Cannot replay from block and use cached events at the same time"

    mgr.cfg.w3 = Web3(Web3.HTTPProvider(mainnet_uri))

    assert (
        mgr.cfg.w3.provider.endpoint_uri == mainnet_uri
    ), f"Failed to connect to Mainnet at {mainnet_uri} - got {mgr.cfg.w3.provider.endpoint_uri} instead"
    mgr.cfg.logger.info(
        "[events.utils.set_network_connection_to_mainnet] Successfully connected to Mainnet"
    )
    mgr.cfg.NETWORK = mgr.cfg.NETWORK_MAINNET


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
        cfg.logger.info(
            f"[events.utils.handle_limit_pairs_for_replay_mode] Limiting replay to pairs: {limit_pairs_for_replay}"
        )
        static_pool_data = static_pool_data[
            static_pool_data["pair_name"].isin(limit_pairs_for_replay)
        ]
    return static_pool_data


def set_network_to_tenderly_if_replay(
    last_block: int,
    loop_idx: int,
    mgr: Any,
    replay_from_block: int,
    tenderly_uri: str or None,
    use_cached_events: bool,
    forked_from_block: int = None,
    tenderly_fork_id: str = None,
) -> Tuple[str or None, int or None]:
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
    tenderly_uri : str or None
        The Tenderly URI
    forked_from_block : int or None
        The block number the Tenderly fork was created from.
    """
    if not replay_from_block and not tenderly_fork_id:
        return None, None

    elif last_block == 0 and tenderly_fork_id:
        mgr.cfg.logger.info(
            f"[events.utils.set_network_to_tenderly_if_replay] Setting network connection to Tenderly idx: {loop_idx}"
        )
        forked_from_block = set_network_connection_to_tenderly(
            mgr=mgr,
            use_cached_events=use_cached_events,
            tenderly_uri=tenderly_uri,
            forked_from_block=forked_from_block,
            tenderly_fork_id=tenderly_fork_id,
        )
        tenderly_uri = mgr.cfg.w3.provider.endpoint_uri
        return tenderly_uri, forked_from_block

    elif replay_from_block and loop_idx > 0 and mgr.cfg.NETWORK != "tenderly":
        # Tx must always be submitted from Tenderly when in replay mode
        mgr.cfg.logger.info(
            f"[events.utils.set_network_to_tenderly_if_replay] Setting network connection to Tenderly idx: {loop_idx}"
        )
        forked_from_block = set_network_connection_to_tenderly(
            mgr=mgr,
            use_cached_events=use_cached_events,
            tenderly_uri=tenderly_uri,
            forked_from_block=forked_from_block,
        )
        mgr.cfg.w3.provider.endpoint_uri = tenderly_uri
        return tenderly_uri, forked_from_block

    else:
        tenderly_uri, forked_from_block = setup_replay_from_block(
            mgr=mgr, block_number=replay_from_block
        )
        mgr.cfg.NETWORK = mgr.cfg.NETWORK_TENDERLY
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

    """
    if (
        (replay_from_block or mgr.tenderly_fork_id)
        and mgr.cfg.NETWORK != "mainnet"
        and last_block != 0
    ):
        mgr.cfg.logger.info(
            f"[events.utils.set_network_to_mainnet_if_replay] Setting network connection to Mainnet idx: {loop_idx}"
        )
        set_network_connection_to_mainnet(
            mgr=mgr,
            use_cached_events=use_cached_events,
            mainnet_uri=mainnet_uri,
        )


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
            f"[events.utils.delete_tenderly_forks] Delete Fork {fork}, Response: {fork_response.status_code}"
        )

    return forks_to_keep

def get_current_block(
    last_block: int,
    mgr: Any,
    reorg_delay: int,
    replay_from_block: int,
    tenderly_fork_id: str,
) -> int:
    """
    Get the current block number, then adjust to the block number reorg_delay blocks ago to avoid reorgs

    Parameters
    ----------
    last_block: int
        The last block
    mgr: Any
        The manager object
    reorg_delay: int
        The number of blocks to wait to avoid reorgs
    replay_from_block: int
        The block number to replay from
    tenderly_fork_id: str
        The Tenderly fork id

    Returns
    -------
    int
        The current block number

    """
    if not replay_from_block and not tenderly_fork_id:
        current_block = mgr.web3.eth.block_number - reorg_delay
    elif last_block == 0 and replay_from_block:
        current_block = replay_from_block - reorg_delay
    elif tenderly_fork_id:
        current_block = mgr.w3_tenderly.eth.block_number
    else:
        current_block = last_block + 1
    return current_block


def handle_static_pools_update(mgr: Any):
    """
    Handles the static pools update 1x at startup and then periodically thereafter upon terraformer runs.

    Parameters
    ----------
    mgr : Any
        The manager object.

    """
    uniswap_v2_event_mappings = pd.DataFrame(
        [
            {"address": k, "exchange_name": v}
            for k, v in mgr.uniswap_v2_event_mappings.items()
        ]
    )
    uniswap_v3_event_mappings = pd.DataFrame(
        [
            {"address": k, "exchange_name": v}
            for k, v in mgr.uniswap_v3_event_mappings.items()
        ]
    )
    solidly_v2_event_mappings = pd.DataFrame(
        [
            {"address": k, "exchange_name": v}
            for k, v in mgr.solidly_v2_event_mappings.items()
        ]
    )
    all_event_mappings = (
        pd.concat([uniswap_v2_event_mappings, uniswap_v3_event_mappings, solidly_v2_event_mappings])
        .drop_duplicates("address")
        .to_dict(orient="records")
    )
    if "uniswap_v2_pools" not in mgr.static_pools:
        mgr.static_pools["uniswap_v2_pools"] = []
    if "uniswap_v3_pools" not in mgr.static_pools:
        mgr.static_pools["uniswap_v3_pools"] = []
    if "solidly_v2_pools" not in mgr.static_pools:
        mgr.static_pools["solidly_v2_pools"] = []

    for ex in mgr.forked_exchanges:
        if ex in mgr.exchanges:
            exchange_pools = [
                e["address"] for e in all_event_mappings if e["exchange_name"] == ex
            ]
            mgr.cfg.logger.info(
                f"[events.utils.handle_static_pools_update] Adding {len(exchange_pools)} {ex} pools to static pools"
            )
            attr_name = f"{ex}_pools"
            mgr.static_pools[attr_name] = exchange_pools


def handle_tokens_csv(mgr, prefix_path, read_only: bool = False):
    tokens_filepath = os.path.normpath(
        f"{prefix_path}fastlane_bot/data/blockchain_data/{mgr.cfg.NETWORK}/tokens.csv"
    )

    try:
        token_data = pd.read_csv(tokens_filepath)
    except Exception as e:
        if not read_only:
            mgr.cfg.logger.info(
                f"[events.utils.handle_tokens_csv] Error reading token data: {e}... creating new file"
            )
            token_data = pd.DataFrame(mgr.tokens)
            token_data.to_csv(tokens_filepath, index=False)
        else:
            raise ReadOnlyException(tokens_filepath) from e

    extra_info = glob(
        os.path.normpath(
            f"{prefix_path}fastlane_bot/data/blockchain_data/{mgr.cfg.NETWORK}/token_detail/*.csv"
        )
    )
    if len(extra_info) > 0:
        extra_info_df = pd.concat(
            [pd.read_csv(f) for f in extra_info], ignore_index=True
        )
        token_data = pd.concat([token_data, extra_info_df], ignore_index=True)
        token_data = token_data.drop_duplicates(subset=["address"])

        if not read_only:
            token_data.to_csv(tokens_filepath, index=False)

            # delete all files in token_detail
            for f in extra_info:
                try:
                    os.remove(f)
                except FileNotFoundError:
                    pass

    mgr.tokens = token_data.to_dict(orient="records")

    mgr.cfg.logger.info(
        f"[events.utils.handle_tokens_csv] Updated token data with {len(extra_info)} new tokens"
    )


def check_and_approve_tokens(cfg: Config, tokens: List):
    """
    This function checks if tokens have been previously approved from the wallet address to the Arbitrage contract.
    If they are not already approved, it will submit approvals for each token specified in Flashloan tokens.

    :param cfg: the config object
    :param tokens: the list of tokens to check/approve

    """
    TxHelpers(cfg=cfg).check_and_approve_tokens(tokens=tokens)
