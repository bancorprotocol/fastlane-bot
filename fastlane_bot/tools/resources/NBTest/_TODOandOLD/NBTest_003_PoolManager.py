# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Unit tests for PoolManager

# + jupyter={"outputs_hidden": false}
import fastlane_bot.db.models as models
from fastlane_bot.db.model_managers import PoolManager, PairManager, TokenManager
from fastlane_bot.db.manager import DatabaseManager

import fastlane_bot.events.exchanges.base
import fastlane_bot.events.pools.base

# +
# Create a ContractHelper instance
pool_manager = PoolManager()

# Print and format version and date
print(f"Version: {pool_manager.__VERSION__.format('0.0.0')}")
print(f"Date: {pool_manager.__DATE__}")

# + jupyter={"outputs_hidden": false}
pair_manager = PairManager()

# Print and format version and date
print(f"Version: {pair_manager.__VERSION__.format('0.0.0')}")
print(f"Date: {pair_manager.__DATE__.format('0.0.0')}")

# + jupyter={"outputs_hidden": false}

# test TokenManager

token_manager = TokenManager()

# Print and format version and date
print(f"Version: {token_manager.__VERSION__.format('0.0.0')}")
print(f"Date: {token_manager.__DATE__.format('0.0.0')}")

# + jupyter={"outputs_hidden": false}

# DatabaseManager

db_manager = DatabaseManager()

# Print and format version and date
print(f"Version: {db_manager.__VERSION__.format('0.0.0')}")
print(f"Date: {db_manager.__DATE__.format('0.0.0')}")

# + jupyter={"outputs_hidden": false}
# Test add_token: Test if a token can be added to the database and if the token has the correct attributes.
token_manager = TokenManager()
token0 = models.Token(address="Test",
                     symbol="Test",
                     name="Test Token",
                     key="Test",
                     decimals=18)

token_manager.create_token(token0)

db_token = token_manager.session.query(models.Token).filter_by(
    address=token0.address).first()

assert db_token is not None
assert db_token.symbol == "Test"
assert db_token.name == "Test Token"
assert db_token.decimals == 18

token1 = models.Token(address="Pair",
                      symbol="Pair",
                      name="Test Token",
                      decimals=18,
                      key="Pair")

token_manager.create_token(token1)

db_token = token_manager.session.query(models.Token).filter_by(
    address=token1.address).first()

assert db_token is not None
assert db_token.symbol == "Pair"
assert db_token.name == "Test Token"
assert db_token.decimals == 18


# + jupyter={"outputs_hidden": false}
from sqlalchemy.orm import Session

# - Test initialization: Ensure that the PoolManager is initialized properly with the given session object.
pair_manager = PairManager()
pool_manager = PoolManager()
assert isinstance(pool_manager.session, Session)
assert isinstance(pair_manager.session, Session)

# + jupyter={"outputs_hidden": false}
# Test add pair
pair_manager = PairManager()
pair = models.Pair(name="Test/Pair",
                   tkn0_address="Test",
                   tkn1_address="Pair",
                   tkn1_key="Pair",
                   tkn0_key="Test"
                   )


pair_manager.create_pair(pair)

db_pair = pair_manager.session.query(models.Pair).filter_by(
    name=pair.name).first()

assert db_pair is not None
assert db_pair.name == "Test/Pair"
assert db_pair.tkn0_address == "Test"
assert db_pair.tkn1_address == "Pair"


# + jupyter={"outputs_hidden": false}
db_manager = DatabaseManager()


blockchain = models.Blockchain(name="TestBlockchain")

db_manager.create(blockchain)

exchange = fastlane_bot.events.exchanges.base.Exchange(name="TestExchange",
                                                       blockchain_name="TestBlockchain")

db_manager.create(exchange)


# + jupyter={"outputs_hidden": false}
# Test add_pool: Test if a pool can be added to the database and if the pool has the correct attributes.
pool_manager = PoolManager()
pool = fastlane_bot.events.pools.base.Pool(id=10000000000,
                                           cid='1x',
                                           pair_name="Test/Pair",
                                           exchange_name="TestExchange",
                                           last_updated_block=10000000000,
                                           address="0x1234567890abcdef1234567890abcdef12345678",
                                           fee=str(0.003))
pool_manager.create_pool(pool)

db_pool = pool_manager.session.query(fastlane_bot.events.pools.base.Pool).filter_by(
    exchange_name=pool.exchange_name,
    pair_name=pool.pair_name).first()
assert db_pool is not None
assert db_pool.pair_name == "Test/Pair"
assert db_pool.exchange_name == "TestExchange"

# + jupyter={"outputs_hidden": false}
# Test get_token
token = pool_manager.get_pool(address="0x1234567890abcdef1234567890abcdef12345678")
assert pool is not None
assert pool.pair_name == "Test/Pair"
assert pool.exchange_name == "TestExchange"

# + jupyter={"outputs_hidden": false}
# Test update_pool
pool = pool_manager.get_pool(address="0x1234567890abcdef1234567890abcdef12345678")
pool_manager.update_pool({"id":pool.id, "address":"Updated Test pool"})

updated_pool = pool_manager.get_pool(id=pool.id)
assert updated_pool is not None
assert updated_pool.address == "Updated Test pool"

# + jupyter={"outputs_hidden": false}
# Test delete_pool
pool = pool_manager.get_pool(address="0x1234567890abcdef1234567890abcdef12345678")
pool_manager.delete_pool(pool)

deleted_pool = pool_manager.get_pool(address="0x1234567890abcdef1234567890abcdef12345678")
assert deleted_pool is None
