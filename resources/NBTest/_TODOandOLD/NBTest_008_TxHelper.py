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

# + jupyter={"outputs_hidden": true}
import requests
from dataclasses import dataclass
from web3 import Web3
from typing import Any, List, Dict, Tuple, Union
import fastlane_bot.config as c


@dataclass
class TxHelper:
    """
    A class to represent a flashloan arbitrage.

    Attributes
    ----------
    usd_gas_limit : float
        The USD gas limit.
    w3 : Web3
        The Web3 instance.
    gas_price_multiplier : float
        The gas price multiplier.
    arb_contract : Any
        The arbitrage contract.
    """
    usd_gas_limit: float = 20
    gas_price_multiplier: float = 1.2
    arb_contract: Any = c.BANCOR_ARBITRAGE_CONTRACT
    w3: Web3 = c.w3

    def __post_init__(self):
        self.PRIVATE_KEY: str = c.ETH_PRIVATE_KEY_BE_CAREFUL
        self.COINGECKO_URL: str = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true'

    @property
    def wallet_address(self) -> str:
        """Get the wallet address.

        Returns:
            str: The wallet address.
        """
        return c.LOCAL_ACCOUNT.address

    @property
    def wallet_balance(self) -> Tuple[Any, int]:
        """Get the wallet balance in Ether.

        Returns:
            float: The wallet balance in Ether.
        """
        balance = self.w3.eth.getBalance(self.wallet_address)
        return balance, self.w3.fromWei(balance, 'ether')

    @property
    def wei_balance(self) -> int:
        """Get the wallet balance in Wei.

        Returns:
            int: The wallet balance in Wei.
        """
        return self.wallet_balance[0]

    @property
    def ether_balance(self) -> float:
        """Get the wallet balance in Ether.

        Returns:
            float: The wallet balance in Ether.
        """
        return self.wallet_balance[1]

    @property
    def nonce(self):
        return c.w3.eth.getTransactionCount(c.LOCAL_ACCOUNT.address)

    @property
    def gas_limit(self):
        return self.get_gas_limit_from_usd(self.usd_gas_limit)

    @property
    def base_gas_price(self):
        """
        Get the base gas price from the Web3 instance.
        """
        return c.w3.eth.gasPrice

    @property
    def gas_price_gwei(self):
        """
        Get the gas price from the Web3 instance (gwei).
        """
        return self.base_gas_price / 1e9

    @property
    def ether_price_usd(self):
        """
        Get the ether price in USD.
        """
        response = requests.get(self.COINGECKO_URL)
        data = response.json()
        return data['ethereum']['usd']

    @property
    def deadline(self):
        return c.w3.eth.getBlock('latest')['timestamp'] + c.DEFAULT_BLOCKTIME_DEVIATION

    def get_gas_limit_from_usd(self, gas_cost_usd: float) -> int:
        """Calculate the gas limit based on the desired gas cost in USD.

        Args:
            gas_cost_usd (float): The desired gas cost in USD.

        Returns:
            int: The calculated gas limit.
        """
        ether_cost = gas_cost_usd / self.ether_price_usd
        gas_limit = ether_cost / self.gas_price_gwei * 1e9
        return int(gas_limit)

    def submit_flashloan_arb_tx(self,
                                arb_data: List[Dict[str, Any]],
                                flashloan_token_address: str,
                                flashloan_amount: int,
                                verbose: bool = True) -> str:

        if not isinstance(flashloan_amount, int):
            flashloan_amount = int(flashloan_amount)

        if flashloan_token_address == c.WETH_ADDRESS:
            flashloan_token_address = c.ETH_ADDRESS

        assert flashloan_token_address != arb_data[0]['targetToken'], \
            "The flashloan token address must be different from the first targetToken address in the arb data."

        if verbose:
            print(f"flashloan amount: {flashloan_amount}")
            print(f"flashloan token address: {flashloan_token_address}")
            print(f"Gas price: {self.gas_price_gwei} gwei")
            print(f"Gas limit in USD ${self.usd_gas_limit} "
                  f"Gas limit: {self.gas_limit} ")

            balance = c.w3.eth.getBalance(c.LOCAL_ACCOUNT.address)
            print(f"Balance of the sender's account: \n"
                  f"{balance} Wei \n"
                  f"{c.w3.fromWei(balance, 'ether')} Ether")

        # Set the gas price (gwei)
        gas_price = int(self.base_gas_price * self.gas_price_multiplier)

        # Prepare the transaction
        transaction = self.arb_contract.functions.flashloanAndArb(
            arb_data, flashloan_token_address, flashloan_amount
        ).buildTransaction(
            {
                'gas': self.gas_limit,
                'gasPrice': gas_price,
                'nonce': self.nonce,
            }
        )

        # Sign the transaction
        signed_txn = c.w3.eth.account.signTransaction(
            transaction, c.ETH_PRIVATE_KEY_BE_CAREFUL
        )

        # Send the transaction
        tx_hash = c.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Transaction sent with hash: {tx_hash}")
        return tx_hash.hex()




# + jupyter={"outputs_hidden": false}
import pytest
from web3 import Web3
from dataclasses import dataclass
from typing import Any, List, Dict, Tuple
from unittest.mock import MagicMock


def create_mock_web3():
    mock_web3 = MagicMock(spec=Web3)
    mock_web3.eth = MagicMock()
    mock_web3.eth.getBalance = MagicMock()
    mock_web3.eth.fromWei = MagicMock()
    return mock_web3


def create_tx_helper(mock_web3):
    return TxHelper(w3=mock_web3)


def test_wallet_address(tx_helper):
    expected_wallet_address = c.LOCAL_ACCOUNT.address

    assert tx_helper.wallet_address == expected_wallet_address

def test_wallet_balance(tx_helper, mock_web3):
    balance_wei = 1000000000000000000
    balance_eth = 1

    mock_web3.eth.getBalance.return_value = balance_wei
    mock_web3.fromWei.return_value = balance_eth

    balance = tx_helper.wallet_balance
    assert balance == (balance_wei, balance_eth)



def test_wei_balance(tx_helper, mock_web3):
    balance_wei = 1000000000000000000

    mock_web3.eth.getBalance.return_value = balance_wei

    assert tx_helper.wei_balance == balance_wei


def test_ether_balance(tx_helper, mock_web3):
    balance_wei = 1000000000000000000
    balance_eth = 1

    mock_web3.eth.getBalance.return_value = balance_wei
    mock_web3.fromWei.return_value = balance_eth

    assert tx_helper.ether_balance == balance_eth

def test_gas_limit(tx_helper, mock_web3):
    expected_gas_limit = 500000
    tx_helper.get_gas_limit_from_usd = MagicMock(return_value=expected_gas_limit)

    assert tx_helper.gas_limit == expected_gas_limit


def test_ether_price_usd(tx_helper):
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {'ethereum': {'usd': 2000}}
        mock_get.return_value = mock_response

        expected_ether_price_usd = 2000
        assert tx_helper.ether_price_usd == expected_ether_price_usd




# + jupyter={"outputs_hidden": false}
from unittest.mock import patch

mock_web3_instance = create_mock_web3()
tx_helper_instance = create_tx_helper(mock_web3_instance)

test_wallet_address(tx_helper_instance)
test_wallet_balance(tx_helper_instance, mock_web3_instance)
test_wei_balance(tx_helper_instance, mock_web3_instance)
test_ether_balance(tx_helper_instance, mock_web3_instance)
test_gas_limit(tx_helper_instance, mock_web3_instance)

with patch('requests.get') as mock_get:
    mock_response = MagicMock()
    mock_response.json.return_value = {'ethereum': {'usd': 2000}}
    mock_get.return_value = mock_response
    test_ether_price_usd(tx_helper_instance)

