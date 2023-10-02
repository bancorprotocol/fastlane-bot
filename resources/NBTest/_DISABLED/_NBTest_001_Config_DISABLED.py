# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
from fastlane_bot.config import Config
import fastlane_bot.config as cfg
from decimal import Decimal
import os

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(cfg.ConfigDB))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(cfg.ConfigNetwork))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(cfg.ConfigProvider))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(cfg.ConfigLogger))
# from carbon.helpers.stdimports import *
# print_version(require="2.4.2")
# -

# # Config [NBTest001]

def raises(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return False
    except Exception as e:
        return str(e)


os.environ["POSTGRES_PASSWORD"] = "b2742bade1f3a271c55eef069e2f19903aa0740c"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_HOST"] = "localhost"


# ## Demo [NOTEST]

C = Config()
#help(C)

#help(C.network)
print(C.network)
C.network.BANCOR_V2_CONVERTER_REGISTRY_ADDRESS, C.BANCOR_V2_CONVERTER_REGISTRY_ADDRESS

#help(C.db)
print(C.db)
C.db.POSTGRES_URL, C.POSTGRES_URL

#help(C.logger)
print(C.logger)
C.logger.logger.info("some info here")
C.logger.LOGLEVEL, C.LOGLEVEL

# ## Basic structure

C = Config()
print(C)
assert str(C) == 'Config(network=_ConfigNetworkMainnet(), db=_ConfigDBPostgres(), logger=_ConfigLoggerDefault(), provider=_ConfigProviderAlchemy())'


# ### Config items at base object

assert C.is_config_item("A") == False
assert C.is_config_item("AA") == False
assert C.is_config_item("AAA") == True
assert C.is_config_item("A_A") == True
assert C.is_config_item("A_1") == True
assert C.is_config_item("a_1") == False
assert C.is_config_item("Aaa") == False
assert C.is_config_item("_AA") == False

assert C.BANCOR_V2_CONVERTER_REGISTRY_ADDRESS == C.network.BANCOR_V2_CONVERTER_REGISTRY_ADDRESS
assert C.POSTGRES_URL == C.db.POSTGRES_URL
assert C.logger.LOGLEVEL == C.LOGLEVEL

# ### ConfigBase

ConfigBase = cfg.base.ConfigBase
class CTest(ConfigBase):
    ITEM1 = 1
    ITEM2 = 2
C=CTest(_direct=False)
CM = CTest(ITEM1=10, ITEM3=3, _direct=False)
assert str(C) == "CTest()"
assert C.ITEM1 == 1
assert C.ITEM2 == 2
assert raises(lambda x: x.ITEM3, C) == "'CTest' object has no attribute 'ITEM3'"
assert CM.ITEM1 == 10
assert CM.ITEM2 == 2
assert CM.ITEM3 == 3

# ### config_new

C = Config.new()
assert C.NETWORK == C.NETWORK_MAINNET
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.PROVIDER == C.PROVIDER_ALCHEMY

C = Config.new(config=Config.CONFIG_MAINNET)
assert C.NETWORK == C.NETWORK_MAINNET
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.PROVIDER == C.PROVIDER_ALCHEMY

C = Config.new(config=Config.CONFIG_UNITTEST)
assert C.NETWORK == C.NETWORK_MAINNET
assert C.DATABASE == C.DATABASE_UNITTEST
assert C.PROVIDER == C.PROVIDER_ALCHEMY

C = Config.new(config=Config.CONFIG_TENDERLY)
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.PROVIDER == C.PROVIDER_TENDERLY

assert str(Config.new().logger.logger) == "<Logger fastlane (INFO)>"
assert str(Config.new(loglevel=Config.LL_DEBUG).logger.logger) == "<Logger fastlane (DEBUG)>"
assert str(Config.new(loglevel=Config.LL_INFO).logger.logger) == "<Logger fastlane (INFO)>"
assert str(Config.new(loglevel=Config.LL_WARN).logger.logger) == "<Logger fastlane (WARNING)>"
assert str(Config.new(loglevel=Config.LL_ERR).logger.logger) == "<Logger fastlane (ERROR)>"
assert str(Config.new(loglevel=Config.LOGLEVEL_DEBUG).logger.logger) == "<Logger fastlane (DEBUG)>"
assert str(Config.new(loglevel=Config.LOGLEVEL_INFO).logger.logger) == "<Logger fastlane (INFO)>"
assert str(Config.new(loglevel=Config.LOGLEVEL_WARNING).logger.logger) == "<Logger fastlane (WARNING)>"
assert str(Config.new(loglevel=Config.LOGLEVEL_ERROR).logger.logger) == "<Logger fastlane (ERROR)>"

# ## Databases

ConfigDB = cfg.ConfigDB
assert issubclass(ConfigDB, cfg.base.ConfigBase)
assert raises(lambda: ConfigDB()) == 'Must instantiate a subclass of ConfigDB via new()'


CAP = ConfigDB.new()
assert issubclass(CAP.__class__, ConfigDB)
assert CAP.__class__.__name__ == '_ConfigDBPostgres'

CAP = ConfigDB.new(ConfigDB.DATABASE_POSTGRES)
assert issubclass(CAP.__class__, ConfigDB)
assert CAP.__class__.__name__ == '_ConfigDBPostgres'
assert CAP.DATABASE == CAP.DATABASE_POSTGRES
assert CAP.POSTGRES_USER == "postgres"
assert CAP.POSTGRES_PASSWORD == "b2742bade1f3a271c55eef069e2f19903aa0740c"
assert CAP.POSTGRES_HOST == "localhost"
assert CAP.POSTGRES_DB == "mainnet"
assert CAP.POSTGRES_URL == 'postgresql://postgres:b2742bade1f3a271c55eef069e2f19903aa0740c@localhost/mainnet'

CAP = ConfigDB.new(ConfigDB.DATABASE_POSTGRES,
                    POSTGRES_USER = "user",
                    POSTGRES_PASSWORD = "password",
                    POSTGRES_HOST = "host",
                    POSTGRES_DB = "db")
assert CAP.DATABASE == CAP.DATABASE_POSTGRES
assert CAP.POSTGRES_USER == "user"
assert CAP.POSTGRES_PASSWORD == "password"
assert CAP.POSTGRES_HOST == "host"
assert CAP.POSTGRES_DB == "db"
assert CAP.POSTGRES_URL == 'postgresql://user:password@host/db'

CAP = ConfigDB.new(ConfigDB.DATABASE_POSTGRES, POSTGRES_URL='postgresql://user:password@host/db')
assert CAP.DATABASE == CAP.DATABASE_POSTGRES
assert CAP.POSTGRES_USER is None
assert CAP.POSTGRES_PASSWORD is None
assert CAP.POSTGRES_HOST is None
assert CAP.POSTGRES_DB is None 
assert CAP.POSTGRES_URL == 'postgresql://user:password@host/db'

assert raises(ConfigDB.new, ConfigDB.DATABASE_SQLITE) == 'Sqlite not implemented'
assert raises(ConfigDB.new, ConfigDB.DATABASE_MEMORY) == 'Memory not implemented'
assert raises(ConfigDB.new, ConfigDB.DATABASE_SDK) == 'SDK not implemented'
assert raises(ConfigDB.new, "meh") == 'Invalid db: meh'

# ## Network

ConfigNetwork = cfg.ConfigNetwork
assert issubclass(ConfigNetwork, cfg.base.ConfigBase)
assert raises(lambda: ConfigNetwork()) == 'Must instantiate a subclass of ConfigNetwork via new()'


# ### Common section

CAM = ConfigNetwork.new()
assert issubclass(CAM.__class__, ConfigNetwork)

# #### COMMONLY USED TOKEN ADDRESSES SECTION

assert CAM.ZERO_ADDRESS == "0x0000000000000000000000000000000000000000"
assert CAM.USDC_ADDRESS == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
assert CAM.MKR_ADDRESS == "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"
assert CAM.LINK_ADDRESS == "0x514910771AF9Ca656af840dff83E8264EcF986CA"
assert CAM.WBTC_ADDRESS == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
assert CAM.ETH_ADDRESS == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
assert CAM.BNT_ADDRESS == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
assert CAM.WETH_ADDRESS == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
assert CAM.WETH_ADDRESS == CAM.WETH9_ADDRESS


# #### ACCOUNTS SECTION

assert CAM.BINANCE8_WALLET_ADDRESS == "0xF977814e90dA44bFA03b6295A0616a897441aceC"
assert CAM.BINANCE14_WALLET_ADDRESS == "0x28c6c06298d514db089934071355e5743bf21d60"

# #### EXCHANGE IDENTIFIERS SECTION

assert CAM.BANCOR_V2_NAME == "bancor_v2"
assert CAM.BANCOR_V3_NAME == "bancor_v3"
assert CAM.UNISWAP_V2_NAME == "uniswap_v2"
assert CAM.UNISWAP_V3_NAME == "uniswap_v3"
assert CAM.SUSHISWAP_V2_NAME == "sushiswap_v2"
assert CAM.CARBON_V1_NAME == "carbon_v1"
assert CAM.EXCHANGE_IDS == {
    'bancor_v2': 1,
    'bancor_v3': 2,
    'uniswap_v2': 3,
    'uniswap_v3': 4,
    'sushiswap_v2': 5,
    'carbon_v1': 6
}
assert CAM.UNI_V2_FORKS == ['uniswap_v2', 'sushiswap_v2']
assert CAM.SUPPORTED_EXCHANGES == list(CAM.EXCHANGE_IDS)

# #### CARBON EVENTS

assert CAM.CARBON_POOL_CREATED == f"{CAM.CARBON_V1_NAME}_PoolCreated"
assert CAM.CARBON_STRATEGY_CREATED == f"{CAM.CARBON_V1_NAME}_StrategyCreated"
assert CAM.CARBON_STRATEGY_DELETED == f"{CAM.CARBON_V1_NAME}_StrategyDeleted"
assert CAM.CARBON_STRATEGY_UPDATED == f"{CAM.CARBON_V1_NAME}_StrategyUpdated"
assert CAM.CARBON_TOKENS_TRADED == f"{CAM.CARBON_V1_NAME}_TokensTraded"

# #### DEFAULT VALUES SECTION

assert CAM.UNIV3_FEE_LIST == [100, 500, 3000, 10000]
assert CAM.MIN_BNT_LIQUIDITY == 2_000_000_000_000_000_000
assert CAM.DEFAULT_GAS == 950_000
assert CAM.DEFAULT_GAS_PRICE == 0
assert CAM.DEFAULT_GAS_PRICE_OFFSET == 1.05
assert CAM.DEFAULT_GAS_SAFETY_OFFSET == 25_000
assert CAM.DEFAULT_POLL_INTERVAL == 12
assert CAM.DEFAULT_BLOCKTIME_DEVIATION == 13 * 500  # 10 block time deviation
assert CAM.DEFAULT_MIN_PROFIT == Decimal("1")
assert CAM.DEFAULT_MAX_SLIPPAGE == Decimal("1")  # 1%
#assert CAM._PROJECT_PATH == os.path.normpath(f"{os.getcwd()}") # TODO: FIX THIS
#assert CAM.DEFAULT_CURVES_DATAFILE == os.path.normpath(f"{_PROJECT_PATH}/carbon/data/curves.csv.gz")
assert CAM.CARBON_STRATEGY_CHUNK_SIZE == 200
assert CAM.Q96 == Decimal("79228162514264337593543950336")
assert CAM.DEFAULT_TIMEOUT == 60
assert CAM.CARBON_FEE == Decimal("0.002")
assert CAM.BANCOR_V3_FEE == Decimal("0.0")
assert CAM.DEFAULT_REWARD_PERCENT == Decimal("0.5")

# #### SUNDRY SECTION

assert CAM.COINGECKO_URL == "https://tokens.coingecko.com/uniswap/all.json"


# ### Mainnet section

# +
CAM = ConfigNetwork.new(ConfigNetwork.NETWORK_MAINNET)
assert issubclass(CAM.__class__, ConfigNetwork)
assert CAM.__class__.__name__ == '_ConfigNetworkMainnet'

# from _ConfigNetworkMainnet object
assert CAM.NETWORK == CAM.NETWORK_ETHEREUM
assert CAM.BANCOR_V3_NETWORK_INFO_ADDRESS == "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
assert CAM.UNISWAP_V2_FACTORY_ADDRESS == "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
assert CAM.UNISWAP_V2_ROUTER_ADDRESS == "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
assert CAM.SUSHISWAP_FACTORY_ADDRESS == "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
assert CAM.UNISWAP_V3_FACTORY_ADDRESS == "0x1F98431c8aD98523631AE4a59f267346ea31F984"
assert CAM.BANCOR_V3_POOL_COLLECTOR_ADDRESS == "0xB67d563287D12B1F41579cB687b04988Ad564C6C"
assert CAM.BANCOR_V2_CONVERTER_REGISTRY_ADDRESS == "0xC0205e203F423Bcd8B2a4d6f8C8A154b0Aa60F19"
assert CAM.FASTLANE_CONTRACT_ADDRESS == "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"
assert CAM.CARBON_CONTROLLER_ADDRESS == "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
assert CAM.CARBON_CONTROLLER_VOUCHER == "0x3660F04B79751e31128f6378eAC70807e38f554E"
assert CAM.MULTICALL_CONTRACT_ADDRESS == "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
# -
# ### Tenderly section

# +
CAT = ConfigNetwork.new(ConfigNetwork.NETWORK_TENDERLY)
assert issubclass(CAT.__class__, ConfigNetwork)
assert CAT.__class__.__name__ == '_ConfigNetworkTenderly'

# from _ConfigNetworkMainnet object
assert CAT.NETWORK == CAT.NETWORK_TENDERLY
assert CAT.BANCOR_V3_NETWORK_INFO_ADDRESS == "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
assert CAT.UNISWAP_V2_FACTORY_ADDRESS == "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
assert CAT.UNISWAP_V2_ROUTER_ADDRESS == "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
assert CAT.SUSHISWAP_FACTORY_ADDRESS == "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
assert CAT.UNISWAP_V3_FACTORY_ADDRESS == "0x1F98431c8aD98523631AE4a59f267346ea31F984"
assert CAT.BANCOR_V3_POOL_COLLECTOR_ADDRESS == "0xB67d563287D12B1F41579cB687b04988Ad564C6C"
assert CAT.BANCOR_V2_CONVERTER_REGISTRY_ADDRESS == "0xC0205e203F423Bcd8B2a4d6f8C8A154b0Aa60F19"
assert CAT.FASTLANE_CONTRACT_ADDRESS == "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"
assert CAT.CARBON_CONTROLLER_ADDRESS == "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
assert CAT.CARBON_CONTROLLER_VOUCHER == "0x3660F04B79751e31128f6378eAC70807e38f554E"
assert CAT.MULTICALL_CONTRACT_ADDRESS == "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
# -

# ### Invalid network

assert raises(ConfigNetwork.new, "meh") == 'Invalid network: meh'

# ## Provider

CN = cfg.ConfigNetwork
CP = cfg.ConfigProvider
assert issubclass(CP, cfg.base.ConfigBase)

# ### Check various combinations of network and provider

# #### Successful

CAP = CP.new(CN.new(CN.NETWORK_ETHEREUM))
assert issubclass(CAP.__class__, CP)
assert CAP.__class__.__name__ == '_ConfigProviderAlchemy'

CAP = CP.new(CN.new(CN.NETWORK_ETHEREUM), provider=CP.PROVIDER_ALCHEMY)
assert CAP.__class__.__name__ == '_ConfigProviderAlchemy'

# +
# CAP = CP.new(CN.new(CN.NETWORK_ETHEREUM), provider=CP.PROVIDER_INFURA)
# assert CAP.__class__.__name__ == '_ConfigProviderInfura'

# +
# CAP = CP.new(CN.new(CN.NETWORK_TENDERLY))
# assert CAP.__class__.__name__ == '_ConfigProviderTenderly'

# +
# CAP = CP.new(CN.new(CN.NETWORK_TENDERLY), provider=CP.PROVIDER_TENDERLY)
# assert CAP.__class__.__name__ == '_ConfigProviderTenderly'
# -

# #### Failing

assert raises(CP.new,CN.new(CN.NETWORK_ETHEREUM), provider=CP.PROVIDER_TENDERLY)
#assert raises(CP.new,CN.new(CN.NETWORK_TENDERLY), provider=CP.PROVIDER_ALCHEMY)
#assert raises(CP.new,CN.new(CN.NETWORK_TENDERLY), provider=CP.PROVIDER_INFURA)

# ### Ethereum via Alchemy

CAP = CP.new(CN.new(CN.NETWORK_ETHEREUM))
assert CAP.network.NETWORK == CN.NETWORK_ETHEREUM
assert CAP.PROVIDER == CP.PROVIDER_ALCHEMY

# ### Ethereum via Infura

# +
# not implemented yet
# -

# ### Tenderly via Tenderly

# +
# not implemented yet
# -

# ### UnitTest

CAP = CP.new(provider=CAP.PROVIDER_UNITTEST, network=CN.new(CN.NETWORK_ETHEREUM))
assert CAP.network.NETWORK == CN.NETWORK_ETHEREUM
assert CAP.PROVIDER == CP.PROVIDER_UNITTEST

# ## Logger

ConfigLogger = cfg.ConfigLogger
assert issubclass(ConfigLogger, cfg.base.ConfigBase)

CAL = ConfigLogger.new()
assert issubclass(CAL.__class__, ConfigLogger)
assert CAL.__class__.__name__ == '_ConfigLoggerDefault'

CAL = ConfigLogger.new(logger=ConfigLogger.LOGGER_DEFAULT)
CAL.logger.debug("debug")
CAL.logger.info("info")
CAL.logger.warning("warning")
CAL.logger.error("error")

# ## Cloaker

# ### General

Cloaker = cfg.cloaker.Cloaker
CloakerL = cfg.cloaker.CloakerL
from dataclasses import dataclass
@dataclass
class TestDC():
    a: int = 1
    b: int = 2
    _c: int = 3
o = TestDC()

co = Cloaker(o)
assert co.a == o.a
assert co.b == o.b
assert co._c == co._ShieldedAttribute(attr='_c', exists=True)
assert raises(lambda x: x._d, co) == "Cloaked[TestDC] has no attribute '_d'"

co = CloakerL(o, visible="b, _c")
assert co.a == co._ShieldedAttribute(attr='a', exists=True)
assert co.b == o.b
assert co._c == o._c
assert co._d == co._ShieldedAttribute(attr='_d', exists=False)

# ### With config object

C = Config().cloaked()
assert C.NETWORK == C._ShieldedAttribute(attr='NETWORK', exists=True)
assert C.NETWORK1 == C._ShieldedAttribute(attr='NETWORK1', exists=False)
assert C.db.__class__.__name__ == "_ConfigDBPostgres"
assert C.ZERO_ADDRESS == '0x0000000000000000000000000000000000000000'

C = Config().cloaked(incl="NETWORK", excl="ZERO_ADDRESS")
assert C.NETWORK == 'ethereum'
assert C.ZERO_ADDRESS == C._ShieldedAttribute(attr='ZERO_ADDRESS', exists=True)


