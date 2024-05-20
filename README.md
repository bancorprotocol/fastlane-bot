# Fastlane Arbitrage Bot

## ⚠️ WARNING: Use at Your Own Risk

The Fastlane Bot requires an Ethereum private key. **Your funds are AT RISK when you run the Fastlane Arbitrage Bot**. Read the _Preparation_ section below. The bot is provided as-is, with the authors and the Bprotocol Foundation not liable for any losses.

## Overview

Arbitrage opportunities occur when token prices between DEXes are imbalanced, and can be closed by making specific trades on the imbalanced DEXes.

The Fastlane is an open-source system that anyone can run, consisting of the Fastlane smart contract, and the Fastlane Arbitrage Bot.

The Fastlane Arbitrage Bot identifies arbitrage opportunities and closes them by executing trades using the Fastlane Smart Contract. The bot can search for opportunities between Carbon and Carbon forks, Bancor, and other DEXes. This enhances market efficiency by aligning Carbon, Carbon forks, and Bancor with market trends.

The system works by executing atomic transactions that take flashloans to fulfill the capital requirements of trades, meaning only gas costs are required to submit transactions.

Permanent URL for this repository: [github.com/bancorprotocol/fastlane-bot][repo]

For frequently asked questions, see [FAQ](resources/FAQ.md).

### Profit Split
Any profit from an arbitrage trade is split between the contract caller & the Protocol. 

### Competition

The Fastlane Arbitrage Bot is competitive in nature. Bot operators compete to close arbitrage opportunities. There are many ways to improve a bot's competitiveness; the following document contains a short list of ideas on how to make a bot more competitive: [How to make your bot competitive](resources/How_to_make_your_bot_competitive.md).


[repo]:https://github.com/bancorprotocol/fastlane-bot

## Getting Started

### Installation

Install Fastlane Arbitrage Bot from PyPi using the following command:

Clone the repo from Bancor's GitHub and install:

```bash
git clone https://github.com/bancorprotocol/fastlane-bot
cd fastlane-bot
pip install poetry
poetry install
```

Once the environment is ready, all commands should be prepended with `poetry run` in order to be executed in the corresponding virtual environment. Alternatively, virtual environment can be activated once using `poetry shell`.

### Legacy Installation (v1.0)
You can access the legacy version of the Fastlane Arbitrage Bot, which was solely designed to facilitate single triangle arbitrage transactions which both initiate and conclude with BNT on the Bancor V3 exchange, by referring to the following link:

[github.com/bancorprotocol/fastlane-bot/releases/tag/v1.0](https://github.com/bancorprotocol/fastlane-bot/releases/tag/v1.0)

### Dependencies
Project depends on `poetry` and `pyproject.toml`. However, in order to preserve backward compatibility, after any change to dependencies, the following command should be run, to update `requirement.txt`
```
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

### Preparation

The Fastlane Arbitrage Bot needs access to an Ethereum wallet's private key. **THIS KEY IS AT RISK AND SHOULD NOT BE USED ELSEWHERE**. Maintain some ETH in the wallet for gas fees and regularly sweep profits. Supply the private key to the bot using an environment variable, as shown:

```bash
set ETH_PRIVATE_KEY_BE_CAREFUL="0x9c..."
```

The bot also needs access to the Ethereum blockchain, preconfigured to use Alchemy. Obtain a free API key from [alchemy.com][alchemy] and supply it to the bot using an environment variable:

```bash
set WEB3_ALCHEMY_PROJECT_ID="0-R5..."
```

[alchemy]:https://www.alchemy.com/

The bot uses [python-dotenv][dotenvev] to load environment variables from a `.env` file in the root directory. However, this is not recommended for security reasons, especially on unencrypted disks.

```bash
export WEB3_ALCHEMY_PROJECT_ID="0-R5..."
export ETH_PRIVATE_KEY_BE_CAREFUL="0x9c..."
export WEB3_ALCHEMY_BASE="api_key_here"
export WEB3_FANTOM="api_key_here"
export WEB3_MANTLE="api_key_here"
export WEB3_LINEA="api_key_here"
```
**Note:** To use the Fantom public RPC, write "public" in place of the API key.

[dotenvev]:https://pypi.org/project/python-dotenv/

### Execution

After installation, run the bot with default parameters using the command:

```bash
poetry run python main.py 
```

### Configuration Options

You can configure the Fastlane Arbitrage Bot using the options in the `@click.option` section of `main.py`. An overview of options is provided below:

- **cache_latest_only** (bool): Whether to cache only the latest events.
- **backdate_pools** (bool): If True, the bot will collect pool data from pools that were not traded on within the number of blocks specified in alchemy_max_block_fetch. This is useful to search pools that are traded infrequently.
- **static_pool_data_filename** (str): The name of the static pool data file. **Recommended not to modify.**
- **arb_mode** (str): Specifies the arbitrage mode. 
  - **Types of arbitrage**: 
    - **Pairwise**: This includes arbitrage trades between two liquidity pools that contain the same tokens. For example: USDC > LINK, LINK > USDC
    - **Triangular**: This includes arbitrage trades between three liquidity pools that can create a triangular route, starting and ending in the same token. For example, USDC > ETH, ETH > LINK, LINK > USDC
    - **Multi**: These modes can trade through multiple Carbon orders as a single trade.
  - **arb_mode options**:
      - **multi_triangle**: Triangular arbitrage between multiple Carbon curves and two other exchange curves.
      - **multi_triangle_complete**: Triangular arbitrage between multiple Carbon curves and two other exchange curves (experimental).
      - **b3_two_hop**: Triangular arbitrage - the same as bancor_v3 mode but more gas-efficient.
      - **multi_pairwise_pol**: Pairwise multi-mode that always routes through the Bancor protocol-owned liquidity contract.
      - **multi_pairwise_all**: **(Default)** Pairwise multi-mode that searches all available exchanges for pairwise arbitrage.
- **flashloan_tokens** (str): Tokens the bot can use for flash loans. Specify token addresses as a comma-separated string (e.g., 0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C, 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2).
- **n_jobs** (int): The number of parallel jobs to run. The default, -1, will use all available cores for the process.
- **exchanges** (str): Comma-separated string of exchanges to include. To include all known forks for Uniswap V2/3, use "uniswap_v2_forks" & "uniswap_v3_forks".
- **polling_interval** (int): Bot's polling interval for new events in seconds. 
- **alchemy_max_block_fetch** (int): Maximum number of blocks to fetch in a single request.
- **reorg_delay** (int): Number of blocks to wait to avoid reorgs.
- **logging_path** (str): The path for log files. **Recommended not to modify.**
- **loglevel** (str): Logging level, which can be DEBUG, INFO, WARNING, or ERROR.
- **use_cached_events** (bool): **Testing option.**  This option runs the bot using historical cached events.
- **randomizer** (int): The bot will randomly select an opportunity from the number of opportunities specified in this configuration after sorting by profit. For example the default setting 3 means the bot will randomly pick one of the 3 most profitable opportunities it found in the randomizer.
- **limit_bancor3_flashloan_tokens** (bool): If True, this limits the flashloan tokens to tokens supported by Bancor V3.
- **default_min_profit_gas_token** (float): The minimum amount of expected profit, denominated in the gas token, to consider executing an arbitrage trade.
- **timeout** (int): **Testing option.** This will stop the bot after the specified amount of time has passed.
- **target_tokens** (str): This option filters pools to only include the tokens specified in this comma-separated list of token addresses. This can be used to significantly limit the scope of the bot.
- **replay_from_block** (int): **Testing option.**  The bot will search the specified historical block & attempt to submit a transaction on Tenderly. This requires a Tenderly account to use. 
- **tenderly_fork_id** (str): **Testing option.** Specified exchanges will be searched on Tenderly.
- **tenderly_event_exchanges** (str): **Testing option.**  Exchanges for which to get events on Tenderly.
- **increment_time** (int): **Testing option.** This option increments the specified amount of time on Tenderly if a value for tenderly_fork_id is provided.
- **increment_blocks** (int): **Testing option.** This option increments the specified number of blocks on Tenderly if a value for tenderly_fork_id is provided.
- **blockchain** (str): The blockchain on which to search for arbitrage. Currently only Ethereum & Base are supported.
- **pool_data_update_frequency** (int): The frequency in bot cycles in which the bot will search for new pools. **Recommended not to modify.**
- **use_specific_exchange_for_target_tokens** (str): This filter will limit pool data to include only tokens contained by the specified exchange. For example "carbon_v1" would limit the scope of pool data to only include pools that have tokens currently traded on Carbon.
- **prefix_path** (str): An optional file path modification, intended for cloud deployment requirements. **Recommended not to modify.**
- **self_fund** (bool): **USE AT YOUR OWN RISK** If set to True, the bot will use funds in the user's wallet to execute trades. Note that upon start, the bot will attempt to set an approval for all tokens specified in the flashloan_tokens field. 


Specify options in the command line. For example:

```bash
poetry run python main.py --arb_mode=multi_pairwise_all --polling_interval=12 --reorg_delay=10 --loglevel=INFO
```

## Troubleshooting

If you encounter import errors or `ModuleNotFound` exceptions, try:

```bash
poetry run python <absolute_path>/main.py
```

## Change Log

We follow [semantic versioning][semver] (`major.minor.patch`), updating the major number for backward incompatible API changes, minor for compatible changes, and patch for minor patches.

[semver]:https://semver.org/

- **v2.0** - Complete rewrite to include Carbon along with Bancor.
- **v1.0** - Initial bot version for Bancor protocol pools only.

### Example Start Configurations
The following examples are command-line inputs that start the bot with different configurations:

#### Bancor V3-focused arbitrage

```commandline
poetry run python main.py --arb_mode=b3_two_hop --alchemy_max_block_fetch=200 --loglevel=INFO --backdate_pools=False --polling_interval=0 --reorg_delay=0 --limit_bancor3_flashloan_tokens=True --randomizer=2 --default_min_profit_gas_token=0.01 --exchanges=carbon_v1,bancor_v3,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3 --flashloan_tokens="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2,0x514910771AF9Ca656af840dff83E8264EcF986CA"
```

#### Carbon-focused pairwise arbitrage
```commandline
poetry run python main.py --arb_mode=multi_pairwise_all --alchemy_max_block_fetch=200 --loglevel=INFO --backdate_pools=False --polling_interval=0 --reorg_delay=0 --default_min_profit_gas_token=0.01 --randomizer=2 --exchanges=bancor_v3,bancor_v2,carbon_v1,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3 --flashloan_tokens="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
```
#### Unfocused pairwise arbitrage
```commandline
poetry run python main.py --arb_mode=multi_pairwise_all --alchemy_max_block_fetch=200 --loglevel=INFO --backdate_pools=False --polling_interval=0 --reorg_delay=0 --default_min_profit_gas_token=0.01 --randomizer=2 --exchanges=bancor_v3,bancor_v2,carbon_v1,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3 --flashloan_tokens="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
```
#### Triangular Carbon-focused arbitrage
```commandline
poetry run python main.py --arb_mode=multi_triangle --alchemy_max_block_fetch=200 --loglevel=INFO --backdate_pools=False --polling_interval=0 --reorg_delay=0 --default_min_profit_gas_token=0.01 --randomizer=2 --exchanges=bancor_v3,bancor_v2,carbon_v1,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3 --flashloan_tokens="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
```