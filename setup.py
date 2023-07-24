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
try:
    assert os.path.exists(env_file), "The .env file is missing. See README.md for instructions"
except AssertionError as e:
    # Create .env file
    print("Creating .env file. Please update it with your environment variables. See README.md for instructions")
    with open(env_file, 'w') as f:
        f.write(f"export WEB3_ALCHEMY_PROJECT_ID=\n")
        f.write(f"export ETH_PRIVATE_KEY_BE_CAREFUL=\n")
        f.write(f"export DEFAULT_MIN_PROFIT_BNT=200\n")
        f.write(f"export ETHERSCAN_TOKEN=\n")
        f.write(f"export TENDERLY_FORK_ID=\n")
        f.write(f"export TENDERLY_ACCESS_KEY=\n")
        f.write(f"export TENDERLY_PROJECT=\n")
        f.write(f"export TENDERLY_USER=\n")

load_dotenv(env_file)

# Check for required variables
required_vars = ['WEB3_ALCHEMY_PROJECT_ID',
                 'ETH_PRIVATE_KEY_BE_CAREFUL',
                 'DEFAULT_MIN_PROFIT_BNT',
                 'ETHERSCAN_TOKEN',
                 'TENDERLY_FORK_ID',
                 'TENDERLY_ACCESS_KEY',
                 'TENDERLY_PROJECT',
                 'TENDERLY_USER']

with open(env_file, 'a') as f:
    for var in required_vars:
        if var not in os.environ:
            print(f"The {var} environment variable is missing in .env file. Adding it with a default empty value. See README.md for instructions")
            if var == 'DEFAULT_MIN_PROFIT_BNT':
                f.write(f"export {var}=1\n")
                os.environ[var] = '1'
            else:
                f.write(f"export {var}=\n")
                os.environ[var] = ''  # Optionally update the current environment as well
        if os.environ[var] == '' and 'TENDERLY' not in var and 'ETHERSCAN_TOKEN' not in var:
            raise Exception(f"The {var} environment variable cannot be None. Please update the .env file. See README.md for instructions")

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
