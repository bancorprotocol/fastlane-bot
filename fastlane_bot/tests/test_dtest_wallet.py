from dataclasses import dataclass
from unittest.mock import MagicMock, patch
import pytest
from web3 import Web3

from fastlane_bot.tests.deterministic.dtest_constants import ETH_ADDRESS
from fastlane_bot.tests.deterministic.dtest_token import TestToken, TestTokenBalance
from fastlane_bot.tests.deterministic.dtest_wallet import TestWallet


@pytest.fixture
def mock_web3():
    mock = MagicMock(spec=Web3)
    eth_mock = MagicMock()
    eth_mock.get_transaction_count = MagicMock(return_value=123)  # Example nonce value
    mock.eth = eth_mock
    return mock

def test_wallet_initialization_with_token_balances(mock_web3):
    # Use a valid Ethereum address for the test token
    valid_eth_address = '0x' + '1' * 40  # Example of a valid Ethereum address
    valid_token_address = '0x' + '2' * 40  # Another example of a valid Ethereum address

    balances = [
        {'token': valid_eth_address, 'balance': 100},  # ETH
        {'token': valid_token_address, 'balance': 200}  # Another token
    ]
    wallet = TestWallet(w3=mock_web3, address=valid_eth_address, balances=balances)

    # Verify that the wallet's balances have been initialized correctly
    assert all(isinstance(balance, TestTokenBalance) for balance in wallet.balances), "Balances should be instances of TestTokenBalance"
    assert all(isinstance(balance.token, TestToken) for balance in wallet.balances), "Tokens should be instances of TestToken"
    assert wallet.balances[0].token.address == Web3.to_checksum_address(valid_eth_address), "Token addresses should be checksummed"
    assert wallet.balances[0].balance == 100, "Balance should be correctly set"


def test_testtoken_initialization_and_contract_assignment(mock_web3):
    token_address = '0x' + '1' * 40  # Example token address
    token = TestToken(token_address)

    assert token.address == Web3.to_checksum_address(token_address), "Token address should be checksummed"

    # Simulate assigning a contract
    mock_contract = MagicMock()
    token.contract = mock_contract
    assert token.contract == mock_contract, "Contract assignment should work correctly"

def test_testtokenbalance_initialization_and_properties(mock_web3):
    token_address = '0x' + '1' * 40
    balance = 100
    token_balance = TestTokenBalance(token=token_address, balance=balance)

    assert isinstance(token_balance.token, TestToken), "Token should be an instance of TestToken"
    assert token_balance.balance == balance, "Balance should be set correctly"
    assert token_balance.hex_balance == Web3.to_hex(balance), "Hex balance should match"

def test_faucet_params_for_eth_and_non_eth(mock_web3):
    eth_token_balance = TestTokenBalance(token=ETH_ADDRESS, balance=100)
    non_eth_token_balance = TestTokenBalance(token='0x' + '2' * 40, balance=200)
    wallet_address = '0x' + '3' * 40

    # ETH token
    eth_params = eth_token_balance.faucet_params(wallet_address)
    assert eth_params[0] == [ETH_ADDRESS], "ETH faucet params should include token address"
    assert eth_params[1] == Web3.to_hex(100), "ETH faucet params should include hex balance"

    # Non-ETH token
    non_eth_params = non_eth_token_balance.faucet_params(wallet_address)
    assert non_eth_params[0] == non_eth_token_balance.token.address, "Non-ETH faucet params should include token address"
    assert non_eth_params[1] == wallet_address, "Non-ETH faucet params should include wallet address"
    assert non_eth_params[2] == Web3.to_hex(200), "Non-ETH faucet params should include hex balance"
