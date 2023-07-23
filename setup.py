# coding=utf-8
"""
Carbon Arbitrage Bot setup.py installer.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""

import re

from setuptools import find_packages, setup

import os
from dotenv import load_dotenv

# Load .env file
env_file = '.env'
assert os.path.exists(env_file), "The .env file is missing. See README.md for instructions"
load_dotenv(env_file)

# Check for required variables
required_vars = ['WEB3_ALCHEMY_PROJECT_ID',
                 'ETH_PRIVATE_KEY_BE_CAREFUL',
                 'ETHERSCAN_TOKEN',
                 'TENDERLY_FORK_ID']

for var in required_vars:
    assert var in os.environ, f"The {var} environment variable is missing in .env file. See README.md for instructions"
    if var != 'TENDERLY_FORK_ID':
        assert os.environ[var], f"The {var} environment variable cannot be blank or None"

import brownie_setup

with open("fastlane_bot/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    )[1]

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras_require = {}
extras_require["complete"] = sorted(set(sum(extras_require.values(), [])))

setup(
    name="fastlane_bot",
    version=version,
    author="Bancor Network",
    author_email="mike@bancor.network",
    description="""
                    Carbon Arbitrage Bot, an open-source arbitrage protocol, allows any user to perform arbitrage between Bancor ecosystem protocols and external exchanges and redirect arbitrage profits back to the protocol.
                """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bancorprotocol/carbon-bot",
    install_requires=open("requirements.txt").readlines(),
    extras_require=extras_require,
    tests_require=["pytest~=6.2.5", "pytest-mock~=3.10.0", "imgkit~=1.2.3"],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">= 3.8, != 3.11.*",
)
