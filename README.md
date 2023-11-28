# Fastlane Arbitrage Bot

## ⚠️ WARNING: Use at Your Own Risk

The Fastlane Bot requires an Ethereum private key. **Your funds are AT RISK when you run the Fastlane Arbitrage Bot**. Read the _Preparation_ section below. The bot is provided as-is, with the authors and the Bprotocol Foundation not liable for any losses.

## Overview

The Fastlane Arbitrage Bot identifies and executes arbitrage opportunities between Carbon, Bancor, and the broader market, enhancing market efficiency by aligning Carbon and Bancor with market trends.

Permanent URL for this repository: [github.com/bancorprotocol/fastlane-bot][repo]

[repo]:https://github.com/bancorprotocol/fastlane-bot

## Getting Started

### Installation

Install Fastlane Arbitrage Bot from PyPi using the following command:

Clone the repo from Bancor's GitHub and install:

```bash
git clone https://github.com/bancorprotocol/fastlane-bot
cd fastlane-bot
pip install -r requirements.txt
python setup.py install
```

Here are the added instructions for Mac users with an Apple Silicon chip:

### Installation for Mac users with Apple Silicon chip

Due to the architectural differences of the Apple Silicon chip, some Python packages may not install correctly using the standard method. Follow the instructions below to create a compatible conda environment, and then install Fastlane Arbitrage Bot:

1. Install Miniforge tailored for Apple Silicon from [here](https://github.com/conda-forge/miniforge#miniforge3).

```bash
# to install miniforge
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
bash Miniforge3-MacOSX-arm64.sh
```

Follow the terminal prompts to ensure conda is installed and initialized.

2. Create a new conda environment using the correct architecture:

```bash
conda create -n fastlane_bot_env python=3.9
conda activate fastlane_bot_env
```

3. Clone the repo from GitHub:

```bash
git clone https://github.com/bancorprotocol/fastlane-bot
cd fastlane-bot
```

3. Now, install Fastlane Arbitrage Bot by using the provided bash scrip `apple-silicon-install.sh`:

```bash
./apple-silicon-install.sh
```

Please note that due to potential compatibility issues with the new Apple Silicon chip, some packages may still fail to install correctly. If you encounter any issues, please report them to the package maintainers.

[sim]:https://github.com/bancorprotocol/carbon-simulator

### Legacy Installation (v1.0)
You can access the legacy version of the Fastlane Arbitrage Bot, which was solely designed to facilitate single triangle arbitrage transactions which both initiate and conclude with BNT on the Bancor V3 exchange, by referring to the following link:

[github.com/bancorprotocol/fastlane-bot/releases/tag/v1.0](https://github.com/bancorprotocol/fastlane-bot/releases/tag/v1.0)

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
```

[dotenvev]:https://pypi.org/project/python-dotenv/

### Execution

After installation, run the bot with default parameters using the command:

```bash
python main.py 
```

### Configuration Options

You can configure the Fastlane Arbitrage Bot using the options in the `@click.option` section of `main.py`. An overview of options is provided below:

- **cache_latest_only** (bool): Whether to cache only the latest events.
- **arb_mode** (str): Specifies the arbitrage mode. 
  - **Types of arbitrage**: 
    - **Pairwise**: This includes arbitrage trades between two liquidity pools that contain the same tokens. For example: USDC > LINK, LINK > USDC
    - **Triangular**: This includes arbitrage trades between three liquidity pools that can create a triangular route, starting and ending in the same token. For example, USDC > ETH, ETH > LINK, LINK > USDC
    - **Multi**: These modes can trade through multiple Carbon orders as a single trade.
  - **arb_mode options**:
      - **single**: Pairwise arbitrage between one Carbon curve and one other exchange curve.
      - **multi** Pairwise arbitrage between **multiple** Carbon curves and one other exchange curve.
      - **triangle**: Triangular arbitrage between one Carbon curve and two other exchange curves.
      - **multi_triangle**: Triangular arbitrage between **multiple** Carbon curves and two other exchange curves.
      - **bancor_v3**: Triangular arbitrage between two Bancor v3 pools and one other exchange curve.
      - **b3_two_hop**: Triangular arbitrage - the same as bancor_v3 mode but more gas-efficient.
      - **multi_pairwise_pol**: Pairwise multi-mode that always routes through the Bancor protocol-owned liquidity contract.
      - **multi_pairwise_bal**: Pairwise multi-mode that always routes through Balancer.
      - **multi_pairwise_all**: **(Default)** Pairwise multi-mode that searches all available exchanges for pairwise arbitrage.
- **flashloan_tokens** (str): Tokens the bot can use for flash loans. Specify tokens as a comma-separated string in TKN-ADDR format (e.g., BNT-FF1C, WETH-6Cc2).
- **exchanges** (str): Comma-separated string of exchanges to include.
- **polling_interval** (int): Bot's polling interval for new events.
- **alchemy_max_block_fetch** (int): Maximum number of blocks to fetch in a single request.
- **reorg_delay** (int): Number of blocks to wait to avoid reorgs.
- **loglevel** (str): Logging level, which can be DEBUG, INFO, WARNING, or ERROR.

Specify options in the command line. For example:

```bash
python main.py --arb_mode=multi --polling_interval=12 --reorg_delay=10 --loglevel=INFO
```

## Troubleshooting

If you encounter import errors or `ModuleNotFound` exceptions, try:

```bash
python <absolute_path>/main.py
```

## Change Log

We follow [semantic versioning][semver] (`major.minor.patch`), updating the major number for backward incompatible API changes, minor for compatible changes, and patch for minor patches.

[semver]:https://semver.org/

- **v2.0** - Complete rewrite to include Carbon along with Bancor.
- **v1.0** - Initial bot version for Bancor protocol pools only.