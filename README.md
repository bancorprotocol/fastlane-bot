# Fastlane Arbitrage Bot

**IMPORTANT WARNING**

The Fastlane Bot requires an Ethereum private key, and **RUNNING THE FASTLANE ARBITRAGE BOT PUTS USER FUNDS AT RISK** (see the section on _Preparation_ below). It is provided on an as-is basis, and neither the authors nor the Bprotocol foundation can be held responsible for any losses. 



## About Fastlane Arbitrage Bot

The Fastlane Arbitrage Bot finds and closes arbitrage opportunities between Carbon, Bancor and the market. This serves to increase market efficiency by ensuring that Carbon and Bancor are in line with the overall market.

The permament URL for this repo is `[github.com/bancorprotocol/fastlane-bot][repo]`.

[repo]:https://github.com/bancorprotocol/fastlane-bot


## Getting started

### Installation

The Fastlane Arbitrage Bot can be installed from PyPi using the command

    pip install fastlane_bot

Alternatively you can clone the repo from the Bancor github

    git clone https://github.com/bancorprotocol/fastlane-bot
    cd fastlane=bot
    pip install -r requirements.txt
    python setup.py install

Apart from a number of standard modules, the bot requires the [Carbon Simulator][sim] installed at a compatible version.

[sim]:https://github.com/bancorprotocol/carbon-simulator


### Preparation

The Fastlane Arbitrage Bot requires acces to the private key of an Ethereum wallet. **ALL FUNDS IN THIS WALLET ARE POTENTIALLY AT RISK AND THIS KEY MUST NOT UNDER ANY CIRCUMSTANCES BE USED ELSEWHERE.** The wallet associated to this key needs some ETH for gas fees, and should be regularly sweeped when profits occur. The private key must be made available to the bot using an environment variable, typically by running a command like

    set ETH_PRIVATE_KEY_BE_CAREFUL="0x9c..."


Running the Fastlane Arbitrage Bot also requires the access to the Ethereum blockchain. It is preconfigured to use Alchemy, and it it requires an Alchemy API key to make network requests. Please go to [alchemy.com][alchemy] for a free API key. This API key must also provided to the bot using an environment variable, eg by running

    set WEB3_ALCHEMY_PROJECT_ID="0-R5..."

[alchemy]:https://www.alchemy.com/

By default, the Fastlane bot uses the default Postgres user and password (postgres:postgres). It is highly recommended to change those default settings after installing Postgres, in which case the username and password should be provided in the environment

    set POSTGRES_USER="..."
    set POSTGRES_PASS="..."

The project uses [dotenvev][dotenvev], so alternatively those variables can be provided in the file called `.env` in the root directory of the arbbot. However, for security reasons this is not recommended, especially on unencrypted disks

    export WEB3_ALCHEMY_PROJECT_ID="0-R5..."
    export ETH_PRIVATE_KEY_BE_CAREFUL="0x9c..."
    export POSTGRES_USER="..."
    export POSTGRES_PASS="..."
    
[dotenvev]:https://pypi.org/project/python-dotenv/

### Execution

Once installed, the Carbon bot can be run using the command

    run_fastlane_bot


Alternatively it can be run using

    cd /path/to/fastlane_bot
    python run.py


### Configurable Options

The Fastlane Arbitrage Bot can be configured to search only for specific exchanges or tokens. These are configured in `run.py`, in the `@click.option` section. 

* __Exchanges:__ To change exchanges, edit the `exchanges` variable, and include/exclude exchange names (found in constants.py), separated by dashes. For example: `@click.option("--tokens", default=f"{ec.BANCOR_V3_NAME}-{ec.UNISWAP_V2_NAME}", type=str)`
* __Tokens:__ To change tokens, edit the `tokens` variable, and include/exclude a string of tokens, separated by dashes. For example: `@click.option("--tokens", default=f"LINK-ETH-WBTC", type=str)`


## Trouble Shooting

If you get import errors or a `ModuleNotFound` exception, try:

````{tab} PyPI
$ python your-local-absolute-path/run.py
````

The Fastlane Arbitrage Bot uses Brownie with Alchemy for some Ethereum network calls. The software is setup to automatically connect to Brownie. However, in the event that you need to manually configure Brownie, follow the steps below:

To configure Brownie with Alchemy, open a terminal in the main project folder, and execute the following commands:

    brownie networks update_provider alchemy https://eth-{}.alchemyapi.io/v2/$WEB3_ALCHEMY_PROJECT_ID

    brownie networks modify mainnet provider=alchemy`

    brownie networks set_provider alchemy

If you receive the error: ValueError: Unable to expand environment variable in host setting: `https:// mainnet.infura.io/v3/$WEB3_INFURA_PROJECT_ID`, try repeating the previous steps, and check [Brownie documentation][bdoc]

[bdoc]:https://eth-brownie.readthedocs.io/en/stable/install.html


## Change log

We attempt to use [semantic versioning][semver] (`major.minor.patch`), so the major number is changed on backward incompatible API changes, the minor number on compatible changes, and the patch number for minor patches.

[semver]:https://semver.org/

- **v2.0** - Complete rewrite of the Fastlane Arbitrage Bot to cover Carbon in addition to Bancor
- **v1.0** - Fastlane bot for Bancor protocol pools only

