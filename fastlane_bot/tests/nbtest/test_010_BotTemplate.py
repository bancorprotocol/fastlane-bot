# ------------------------------------------------------------
# Auto generated test file `test_010_BotTemplate.py`
# ------------------------------------------------------------
# source file   = NBTest_010_BotTemplate.py
# source path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# test id       = 010
# test comment  = BotTemplate
# ------------------------------------------------------------



from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider, Bot
from web3 import Web3
from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *

from fastlane_bot import __VERSION__
require("2.0", __VERSION__)






# ------------------------------------------------------------
# Test      010
# File      test_010_BotTemplate.py
# Segment   Mainnet Alchemy [NOTEST]
# ------------------------------------------------------------
def notest_mainnet_alchemy():
# ------------------------------------------------------------
    
    C = Config.new(config=Config.CONFIG_MAINNET)
    assert C.DATABASE == C.DATABASE_POSTGRES
    assert C.POSTGRES_DB == "mainnet"
    assert C.NETWORK == C.NETWORK_MAINNET
    assert C.PROVIDER == C.PROVIDER_ALCHEMY
    print("Web3 API:", C.w3.api)
    

# ------------------------------------------------------------
# Test      010
# File      test_010_BotTemplate.py
# Segment   Mainnet Alchemy Configuration
# ------------------------------------------------------------
def test_mainnet_alchemy_configuration():
# ------------------------------------------------------------
    
    C = Config.new(config=Config.CONFIG_MAINNET)
    assert C.DATABASE == C.DATABASE_POSTGRES
    assert C.POSTGRES_DB == "mainnet"
    assert C.NETWORK == C.NETWORK_MAINNET
    assert C.PROVIDER == C.PROVIDER_ALCHEMY
    assert C.w3.__class__.__name__ == "Web3"
    assert C.w3.isConnected()
    assert C.w3.provider.endpoint_uri.startswith("https://eth-mainnet.alchemyapi.io/v2")
    
    bot = Bot(ConfigObj=C)
    
    # +
    # bot.update_pools()
    
    # +
    # bot.drop_tables()
    # -
    
    
    
    

# ------------------------------------------------------------
# Test      010
# File      test_010_BotTemplate.py
# Segment   Unittest Configuration
# ------------------------------------------------------------
def test_unittest_configuration():
# ------------------------------------------------------------
    
    C = Config.new(config=Config.CONFIG_UNITTEST)
    assert C.DATABASE == C.DATABASE_UNITTEST
    assert C.NETWORK == C.NETWORK_MAINNET
    assert C.PROVIDER == C.PROVIDER_UNITTEST
    
    