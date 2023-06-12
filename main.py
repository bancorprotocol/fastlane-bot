import json
import logging
import os
import time
from typing import List, Any, Tuple, Hashable

import brownie
import click
import pandas as pd
from dotenv import load_dotenv
from joblib import Parallel, delayed

from fastlane_bot.bot import CarbonBot
from fastlane_bot.config import Config
from fastlane_bot.data_fetcher.interface import QueryInterface
from fastlane_bot.data_fetcher.manager import Manager
from fastlane_bot.data_fetcher.utils import complex_handler, filter_latest_events

load_dotenv()


@click.command()
@click.option(
    "--cache_latest_only",
    default=True,
    type=bool,
    help="Set to True for production. Set to False for " "testing / debugging",
)
@click.option(
    "--backdate_pools",
    default=True,
    type=bool,
    help="Set to False for faster testing / debugging",
)
@click.option(
    "--static_pool_data_filename",
    default="static_pool_data",
    help="Filename of the static pool data.",
)
@click.option("--arb_mode", default="single", type=str, help="See arb_mode in bot.py")
@click.option(
    "--flashloan_tokens", default=None, type=str, help="See flashloan_tokens in bot.py"
)
@click.option("--config", default=None, type=str, help="See config in config/*")
@click.option("--n_jobs", default=-1, help="Number of parallel jobs to run")
@click.option(
    "--exchanges",
    default="uniswap_v3,uniswap_v2,carbon_v1,bancor_v3",
    # default="carbon_v1,bancor_v3,uniswap_v3",
    help="Comma separated external exchanges",
)
@click.option(
    "--polling_interval",
    default=12,
    help="Polling interval in seconds",
)
@click.option(
    "--alchemy_max_block_fetch",
    default=2000,
    help="Max number of blocks to fetch from alchemy",
)
@click.option(
    "--reorg_delay",
    default=2,
    help="Number of blocks delayed to avoid reorgs",
)
@click.option(
    "--dbfs_path",
    default='/dbfs/FileStore/tables/carbonbot/logs/',
    help="The Databricks logging path.",
)
def main(
        cache_latest_only: bool,
        backdate_pools: bool,
        arb_mode: str,
        flashloan_tokens: str,
        config: str,
        n_jobs: int,
        exchanges: str,
        polling_interval: int,
        alchemy_max_block_fetch: int,
        static_pool_data_filename: str,
        reorg_delay: int,
        dbfs_path: str,
):
    """
    The main entry point of the program. It sets up the configuration, initializes the web3 and Manager objects,
    adds initial pools to the Manager and then calls the `run` function.

    Args:
        cache_latest_only (bool): Whether to cache only the latest events or not.
        backdate_pools (bool): Whether to backdate pools or not. Set to False for quicker testing runs.
        arb_mode (str): The arbitrage mode to use.
        flashloan_tokens (str): Tokens that the bot can use for flash loans.
        config (str): The name of the configuration to use.
        n_jobs (int): The number of jobs to run in parallel.
        exchanges (str): A comma-separated string of exchanges to include.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        static_pool_data_filename (str): The filename of the static pool data to read from.
        reorg_delay (int): The number of blocks to wait to avoid reorgs.
        dbfs_path (str): The Databricks logging path.
    """
    # Set config
    if config and config == "tenderly":
        cfg = Config.new(config=Config.CONFIG_TENDERLY)
        cfg.logger.info("Using Tenderly config")
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET)
        cfg.logger.info("Using mainnet config")

    # Set external exchanges
    exchanges = exchanges.split(",")
    cfg.logger.info(f"Running data fetching for exchanges: {exchanges}")

    # Check if CSV file exists
    if not os.path.isfile(f"fastlane_bot/data/{static_pool_data_filename}.csv"):
        cfg.logger.error("CSV file does not exist")
        raise FileNotFoundError("CSV file does not exist")

    # Read static pool data from CSV
    try:
        static_pool_data = pd.read_csv(
            f"fastlane_bot/data/{static_pool_data_filename}.csv", low_memory=False
        )
        static_pool_data = static_pool_data[
            static_pool_data["exchange_name"].isin(exchanges)
        ]
    except pd.errors.ParserError:
        cfg.logger.error("Error parsing the CSV file")
        raise

    # Initialize web3
    static_pool_data["cid"] = [
        cfg.w3.keccak(text=f"{row['descr']}").hex()
        for index, row in static_pool_data.iterrows()
    ]

    print('WETH-6Cc2/USDT-1ec7', static_pool_data[static_pool_data['pair_name'] == 'WETH-6Cc2/USDT-1ec7'][['cid', 'address']].values[0])

    add = ['0x92d16588e9E7cef68C0a5F043bED5146b6120E38', '0xbe8BC29765E11894f803906Ee1055a344fDf2511', '0xdC720cF93422D2eC32FC87F19a03D9EfE0159491', '0x040bEf6A2984Ba28D8AF8A24dDb51D61fbF08A81', '0xd371a5C044Aaa65023Db93a5F04443250c8457A8', '0x811559D11DC36d263c34959b980A4E1Bea7cBbe7', '0x360d64B4a0E27A06F0efC812c4c605F0a9CBcf5b', '0x43A372e4dad9D28E476C5a591810981895511f8A', '0x1Ae7308F87caFB782D8f8b0d657bE00BB92020dC', '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc', '0xDc5811d9aE364e095FC19c0035807A0C13213014', '0x40643d019BcB381800F0C2D593a4a6472cCd7493', '0x0387e56B85e6DBAc5586c74cFd089F03922CF3De', '0xfE17Ab3F63038B3b5BC400d6691B2f4d50A33Bf0', '0x4FF4c7c8754127Cc097910cf9D80400ADEf5b65d', '0x6e3F06Fd0dA1c968b6d413576526A597bfD7171B', '0x29C827Ce49aCCF68A1a278C67C9D30c52fBbC348', '0xc5eA9262bECc6E626875b6afa40E2815c4d8253c', '0xb7269C59cE76AbCee44F93FCfC2B1D3e61a631F4', '0x9da85BB6845Dd9063B308DFB41D228dEc78f84a9', '0x8328C886cd4176759BFc4a6a8f9C6973cfEe3D65', '0xD3015D91F9d38a425FA31bc621599D39F5B34eA8', '0xd9721c4fAB2638Fdeb4De788C0c6bEa657164F8E', '0xC948373c672000dEDF16c42FA405BBEA98333d1C', '0xF932fF2B8E73FC5B3543F605b34e9bdf4b12001B', '0xF827FA9B46745A876637406e2A3bf0a2766B89BA', '0x442D8eBAA682eaE1e0218C483E70F1D179Db7A4F', '0x90eF6845C2D22201A5407eAe821957d9B70aa396', '0xE342253d5a0c1AC9DA0203b0256E33c5CFe084f0', '0xee0E362ec1c2422662eCf938dB29F187437cF7B5', '0xD40C3016791BF8Ae0A21F56939a85599CF945a26', '0x2F16c1Ad5071491E9c715103Dd71E637EA45730b', '0x86545700C2456B22a8c8c4346970c01601Da77ff', '0xc8DC4aC3CaF5b317d0D6f63c0e1f18EdEE41f6f4', '0x694c46A27657Da9f9e45053f5116ac6856F71627', '0x6155C81DB52A4C6628c559Be0Af10F6d87BB7d2e', '0x938a0764B7c07f3FD85A0f00536F4439b1401FEf', '0x424485f89ea52839fdB30640Eb7DD7E0078E12fb', '0x7620Df3b01FfF633a5eF8d89d68e88dEb6d37807', '0x3eE8761F561E61a42b99E0C0349717cAEFddDDA1', '0x5eCc8b912b698F7CA1d4Fd1e656e49D10AF0A3F0', '0xB5b7E53424373342F5E73a5986011C8eD9177409', '0x8f1B19622a888c53C8eE4F7D7B4Dc8F574ff9068', '0x5fd8C4738743ae585654D39DeBefBa9e348340F3', '0x04411209D86e742Ec3e94af868Cb050EdB594d37', '0xDA7cF6a0CD5d5e8D10AB55d8bA58257813a239cA', '0x5417c43A64d75FC90E2A84FCBE6Df2124Ea83d55', '0x6423f3fce7991A5E38140EC777E081cfA8aa11d0', '0x9Daeb0A1849D57f6BEBe0e5969644950f0689936', '0xA56b474CA8147BFD243e07801485deBf72e98239', '0x2d3BB204c48e7aC6E2fb3D9F15107869e32cF951', '0x3A925503970D40D36D2329e3846E09fcfc9b6aCB', '0xAA665aD2C5f99C9861C1030Ef85e48BA07059c2A', '0xd4e7a6e2D03e4e48DfC27dd3f46DF1c176647E38', '0x8EeaE625615eD5acc8b96a8f26C228FF51bf2Df9', '0x306eeaff376A128514e40B4846E1650d9Ba7Ae43', '0x8296d84E911e0c1F827E1E7d4B50c2568E807B36', '0x8Acb8B7F910c5de4Cb62DaE334047283D9A3286F', '0xD9E0CEB368FA446188D78A60F64a02D46e089E28', '0x1e8c7b2Ed1c48d03f0bb348e58528d50af506BA9', '0xf3867885c47f5b4363908E77Fa734e39ACe87eDf', '0x9d680D9D67eD745ad186b82cD880795a5deF2f52', '0x09b1C9539cA1Bb440Cc37704bFd7509B208Eb5CC', '0xf3488607490032B594bA2969DB44432E1149E3e4', '0xF3078Ee0D567875AB484671C411e14c964a789b0', '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852']
    print(static_pool_data[static_pool_data['address'].isin(add)]['pair_name'].unique())

    # Initialize data fetch manager
    mgr = Manager(
        web3=cfg.w3,
        cfg=cfg,
        pool_data=static_pool_data.to_dict(orient="records"),
        SUPPORTED_EXCHANGES=exchanges,
        alchemy_max_block_fetch=alchemy_max_block_fetch,
    )

    # Add initial pools for each row in the static_pool_data
    start_time = time.time()
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(mgr.add_pool_to_exchange)(row) for row in mgr.pool_data
    )
    cfg.logger.info(f"Time taken to add initial pools: {time.time() - start_time}")

    # Run the main loop
    run(
        cache_latest_only,
        backdate_pools,
        mgr,
        n_jobs,
        polling_interval,
        alchemy_max_block_fetch,
        arb_mode,
        flashloan_tokens,
        reorg_delay,
        dbfs_path
    )


def run(
        cache_latest_only: bool,
        backdate_pools: bool,
        mgr: Manager,
        n_jobs: int,
        polling_interval: int,
        alchemy_max_block_fetch: int,
        arb_mode: str,
        flashloan_tokens: List[str] or None,
        reorg_delay: int,
        dbfs_path: str
) -> None:
    """
    The main function that drives the logic of the program. It uses helper functions to handle specific tasks.

    Args:
        cache_latest_only (bool): Whether to cache only the latest events or not.
        backdate_pools (bool): Whether to backdate pools or not. Set to False for quicker testing runs.
        mgr (Manager): The manager object that is responsible for handling events and updating pools.
        n_jobs (int): The number of jobs to run in parallel.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        arb_mode (str): The arbitrage mode to use.
        flashloan_tokens (List[str]): List of tokens that the bot can use for flash loans.
        reorg_delay (int): The number of blocks to wait to avoid reorgs.
        dbfs_path (str): The path to the DBFS directory.
    """

    def get_event_filters(start_block: int, current_block: int) -> Any:
        """
        Creates event filters for the specified block range.

        Args:
            start_block (int): The starting block number for the event filters.
            current_block (int): The current block number for the event filters.

        Returns:
            Any: A list of event filters.
        """
        return Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(event.createFilter)(fromBlock=start_block, toBlock=current_block)
            for event in mgr.events
        )

    def get_all_events(event_filters: Any) -> List[Any]:
        """
        Fetches all events using the given event filters.

        Args:
            event_filters (Any): A list of event filters to use.

        Returns:
            List[Any]: A nested list of all fetched events.
        """
        return Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(event_filter.get_all_entries)() for event_filter in event_filters
        )

    def save_events_to_json(
            latest_events: List[Any], start_block: int, current_block: int
    ) -> None:
        """
        Saves the given events to a JSON file.

        Args:
            latest_events (List[Any]): A list of the latest events to save.
            start_block (int): The starting block number of the events.
            current_block (int): The current block number of the events.
        """
        if cache_latest_only:
            path = f"{dbfs_path}latest_event_data.json"
        else:
            path = f"event_data/{mgr.SUPPORTED_EXCHANGES}_{start_block}_{current_block}.json"
        try:
            with open(path, "w") as f:
                latest_events = [_['args'].pop('contextId', None) for _ in latest_events] and latest_events
                f.write(json.dumps(latest_events))
        except Exception as e:
            mgr.cfg.logger.error(f"Error saving events to JSON: {e}")

    def update_pools_from_events(latest_events: List[Any]) -> None:
        """
        Updates the pools with the given events.

        Args:
            latest_events (List[Any]): A list of the latest events.
        """
        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(mgr.update)(event=event) for event in latest_events
        )

    def update_pools_directly_from_contracts(rows_to_update: List[int]) -> None:
        """
        Updates the pools directly from the contracts.

        Args:
            rows_to_update (List[int]): A list of indices of rows to update.
        """
        with brownie.multicall(address=mgr.cfg.MULTICALL_CONTRACT_ADDRESS):
            Parallel(n_jobs=n_jobs, backend="threading")(
                delayed(mgr.update)(pool_info=mgr.pool_data[idx])
                for idx in rows_to_update
            )

    def write_pool_data_to_disk(current_block: int) -> None:
        """
        Writes the pool data to disk.

        Args:
            current_block (int): The current block number.
        """
        if cache_latest_only:
            path = f"{dbfs_path}latest_pool_data.json"
        else:
            path = f"pool_data/{mgr.SUPPORTED_EXCHANGES}_{current_block}.json"
        try:
            with open(path, "w") as f:
                f.write(json.dumps(mgr.pool_data))
        except Exception as e:
            mgr.cfg.logger.error(f"Error writing pool data to disk: {e}")

    def parse_bancor3_rows_to_update(rows_to_update: List[Hashable]) -> Tuple[List[Hashable], List[Hashable]]:
        """
        Parses the rows to update for Bancor v3 pools.

        Args:
            rows_to_update (List[int]): A list of indices of rows to update.

        Returns:
            Tuple[List[str], List[str]]: A tuple of lists of Bancor v3 pool addresses and other pool addresses.
        """
        bancor3_pool_rows = [
            idx for idx in rows_to_update if
            mgr.pool_data[idx]["exchange_name"] == "bancor_v3"
        ]
        other_pool_rows = [
            idx for idx in rows_to_update if
            mgr.pool_data[idx]["exchange_name"] != "bancor_v3"
        ]
        return bancor3_pool_rows, other_pool_rows

    def init_bot(mgr: Manager) -> CarbonBot:
        """
        Initializes the bot.

        Parameters
        ----------
        mgr : Manager
            The manager object.

        Returns
        -------
        CarbonBot
            The bot object.
        """
        mgr.cfg.logger.info("Initializing the bot...")
        crosscheck = pd.read_csv(
            f"fastlane_bot/data/pools_crosscheck.csv", low_memory=False
        )
        db = QueryInterface(ConfigObj=mgr.cfg, state=mgr.pool_data, crosscheck=crosscheck)
        bot = CarbonBot(ConfigObj=mgr.cfg)
        bot.db = db
        assert isinstance(
            bot.db, QueryInterface
        ), "QueryInterface not initialized correctly"
        return bot

    loop_idx = last_block = 0
    while True:
        try:

            # Save initial state of pool data to assert whether it has changed
            initial_state = mgr.pool_data.copy()

            # Get current block number, then adjust to the block number reorg_delay blocks ago to avoid reorgs
            current_block = max([block['last_updated_block'] for block in mgr.pool_data]) if last_block != 0 else mgr.web3.eth.blockNumber - reorg_delay

            # Get all events from the last block to the current block
            start_block = (
                max(0, current_block - (alchemy_max_block_fetch-2))
                if last_block == 0
                else current_block - 1
            )

            mgr.cfg.logger.info(f"Fetching events from {start_block} to {current_block}... {last_block}")

            # Get all event filters, events, and flatten them
            events = [
                complex_handler(event)
                for event in [
                    complex_handler(event)
                    for event in get_all_events(
                        get_event_filters(start_block, current_block)
                    )
                ]
            ]

            # Filter out the latest events per pool, save them to disk, and update the pools
            latest_events = filter_latest_events(mgr, events)
            mgr.cfg.logger.info(f"Found {len(latest_events)} new events")

            save_events_to_json(latest_events, start_block, current_block)
            update_pools_from_events(latest_events)

            # Assert that all the pools in the event data have been updated
            unique_pools_in_events = {event["address"] for event in latest_events}
            unique_pools_in_pool_data = {pool["address"] for pool in mgr.pool_data}
            if not all(pool_address in unique_pools_in_pool_data for pool_address in unique_pools_in_events):
                mgr.cfg.logger.warning(f"Not all pools in the event data have been updated")

            # If this is the first iteration, update all pools without a recent event from the contracts
            if last_block == 0 and backdate_pools:
                rows_to_update = mgr.get_rows_to_update(start_block)
                rows_to_update += [idx for idx, pool in enumerate(mgr.pool_data) if pool['pair_name'] == 'BNT-FF1C/ETH-EEeE' and pool['exchange_name'] == 'bancor_v3']

                # Because we use Bancor3 pools for pricing, we want to update them all on the initial pass.
                bancor3_pool_rows, other_pool_rows = parse_bancor3_rows_to_update(rows_to_update)
                for rows_to_update in [bancor3_pool_rows, other_pool_rows]:
                    update_pools_directly_from_contracts(rows_to_update)

            # Update the last block and write the pool data to disk for debugging, and to backup the state
            last_block = current_block
            write_pool_data_to_disk(current_block)

            # Delete and re-initialize the bot (ensures that the bot is using the latest pool data)
            del bot
            bot = init_bot(mgr)

            # Compare the initial state to the final state, and update the state if it has changed
            final_state = mgr.pool_data.copy()
            assert bot.db.state == final_state, "\n *** bot failed to update state *** \n"
            if initial_state != final_state:
                mgr.cfg.logger.info("State has changed...")

            bot.db.handle_token_key_cleanup()

            # Remove zero liquidity pools
            if loop_idx > 0:
                bot.db.remove_zero_liquidity_pools()

            # Increment the loop index
            loop_idx += 1

            # Run the bot
            bot.run(
                polling_interval=polling_interval,
                flashloan_tokens=flashloan_tokens,
                mode="single",
                arb_mode=arb_mode,
            )

            # Sleep for the polling interval
            time.sleep(polling_interval)

        except Exception as e:
            mgr.cfg.logger.error(f"Error in main loop: {e}")
            time.sleep(polling_interval)


if __name__ == "__main__":
    main()
