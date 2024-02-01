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

# # Unit tests for TokenManager

# + jupyter={"outputs_hidden": false}
import fastlane_bot.db.models as models
from fastlane_bot.db.model_managers import TokenManager

# +
# Create a ContractHelper instance
token_manager = TokenManager()

# Print and format version and date
print(f"Version: {token_manager.__VERSION__.format('0.0.0')}")
print(f"Date: {token_manager.__DATE__}")

# + jupyter={"outputs_hidden": false}
from sqlalchemy.orm import Session

# Test initialization
token_manager = TokenManager()
assert isinstance(token_manager.session, Session)

# + jupyter={"outputs_hidden": false}
# Test add_token
token_manager = TokenManager()
token = models.Token(symbol="TEST", name="Test Token", address="0x1234567890abcdef1234567890abcdef12345678", decimals=18, key="TEST-5678")
token_manager.create_token(token)

db_token = token_manager.session.query(models.Token).filter_by(address=token.address).first()
assert db_token is not None
assert db_token.symbol == "TEST"
assert db_token.name == "Test Token"
assert db_token.address == "0x1234567890abcdef1234567890abcdef12345678"
assert db_token.decimals == 18
assert db_token.key == "TEST-5678"

# + jupyter={"outputs_hidden": false}
# Test get_token
token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
assert token is not None
assert token.symbol == "TEST"

# + jupyter={"outputs_hidden": false}
# Test update_token
token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
token_manager.update_token(token, new_data={"name":"Updated Test Token"})

updated_token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
assert updated_token is not None
assert updated_token.name == "Updated Test Token"

# + jupyter={"outputs_hidden": false}
# Test delete_token
token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
token_manager.delete_token(token)

deleted_token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
assert deleted_token is None
