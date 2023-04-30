# ------------------------------------------------------------
# Auto generated test file `test_004_TokenManager.py`
# ------------------------------------------------------------
# source file   = NBTest_004_TokenManager.py
# source path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# test id       = 004
# test comment  = TokenManager
# ------------------------------------------------------------





import fastlane_bot.db.models as models
from fastlane_bot.db.model_managers import TokenManager

token_manager = TokenManager()

print(f"Version: {token_manager.__VERSION__.format('0.0.0')}")
print(f"Date: {token_manager.__DATE__}")

from sqlalchemy.orm import Session

token_manager = TokenManager()
assert isinstance(token_manager.session, Session)

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

token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
assert token is not None
assert token.symbol == "TEST"

token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
token_manager.update_token(token, new_data={"name":"Updated Test Token"})

updated_token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
assert updated_token is not None
assert updated_token.name == "Updated Test Token"

token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
token_manager.delete_token(token)

deleted_token = token_manager.get_token(address="0x1234567890abcdef1234567890abcdef12345678")
assert deleted_token is None