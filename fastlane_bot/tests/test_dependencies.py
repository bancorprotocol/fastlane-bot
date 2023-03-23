# test_exceptions.py

"""
Code Analysis:
-- NA
"""
import os

"""
Test Plan:
- def test_brownie_version(): tests that the brownie version is correct. Test uses [brownie._config.__version__]
- test_joblib_version(): tests that the joblib version is correct. Test uses [joblib.__version__]
- test_click_version(): tests that the click version is correct. Test uses [click.__version__]
- test_pandas_version(): tests that the pandas version is correct. Test uses [pandas.__version__]
- test_dotenv_version(): tests that the dotenv version is correct. Test uses [dotenv.version.__version__]
- test_pyarrow_version(): tests that the pyarrow version is correct. Test uses [pyarrow.__version__]
- test_pytest_version(): tests that the pytest version is correct. Test uses [pytest.__version__]
- test_etherium_constants(): tests that the ethereum constants are correct. Test uses [fastlane_bot.constants.ec]
"""

import brownie
import click
import dotenv
import joblib
import pandas
import pyarrow
import pytest
from fastlane_bot.utils import check_paths

dotenv.load_dotenv()

p = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", ""))
check_paths(p)


def test_brownie_version():
    assert brownie._config.__version__ == "1.19.3"


def test_joblib_version():
    assert joblib.__version__ == "1.2.0"


def test_click_version():
    assert click.__version__ == "8.1.3"


def test_pandas_version():
    assert pandas.__version__ in ["1.5.2", "1.5.3"]


def test_dotenv_version():
    from dotenv import version

    assert version.__version__ == "0.16.0"


def test_pyarrow_version():
    assert pyarrow.__version__ == "11.0.0"


def test_pytest_version():
    assert pytest.__version__ == "6.2.5"


def test_etherium_constants():
    from fastlane_bot.constants import ec

    assert isinstance(ec.DB, pandas.DataFrame)
    assert ec.DB.shape[0] > 0
    assert ec.DB.shape[1] > 0
    assert ec.DB["exchange"].nunique() > 0
    assert ec.DB["pair"].nunique() > 0
    assert ec.DB["address"].nunique() > 0
    assert ec.DB["fee"].nunique() > 0
    assert ec.DB["symbol0"].nunique() > 0
    assert ec.DB["symbol1"].nunique() > 0
    assert ec.DB["decimal0"].nunique() > 0
    assert ec.DB["decimal1"].nunique() > 0
    assert ec.DB["address0"].nunique() > 0
    assert ec.DB["address1"].nunique() > 0

    assert len(ec.SUPPORTED_TOKENS) > 0
    assert len(ec.SUPPORTED_EXCHANGES) > 0
