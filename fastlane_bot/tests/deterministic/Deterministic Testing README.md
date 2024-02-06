# Deterministic Testing README
## Purpose
The purpose of this testing framework is to have a reproducible and deterministic method for testing essential arb bot functions. Initially, this is focused toward support for Carbon and the Bancor Ecosystem.

***Note this test suite requires Tenderly TestNets***
## Running the Test
1) Simply run `Deterministic_test.ipynb`
## Overview of Process
The current order of the process is as follows:
1) Prepare Carbon blank state
1) Set state on external pools of interest
1) Start bot
1) Create new Carbon strategies
1) Await successful transactions and verify executed arbs exactly match expected results
## Instructions for Use
Each test is comprised of:
1) Static pool data for importing relevant pools and setting state `fastlane_bot\data\blockchain_data\ethereum\static_pool_data_testing.csv`
1) Carbon strategy(s) to arb against `fastlane_bot\data\blockchain_data\ethereum\test_strategies.json`
1) The expected results of the arb transaction `fastlane_bot\data\blockchain_data\ethereum\test_results.json`
## Detailed Process
For reliable execution each step in the process needs to be explictly controlled. For this, the aim is to achieve a Carbon protocol-wide state containing only relevant test strategies and import data for only the relevant external pools for executing arbs.
1) The test can be run on either a current Tenderly testnet deployment (by specifying the url and fromBlock) or can automatedly create a new testnet forking from mainnet. For the latter, please ensure the correct information is added to your `.env` for `TENDERLY_ACCESS_KEY`, `TENDERLY_PROJECT`, and `TENDERLY_USER`
1) The Carbon protocol is cleared by deleting all strategies (note that there are some tax-token strategies that require special handling)
1) The state of external pools is modified by updating the slot data and setting the desired tokens balances on that pool. This is typically done by inspecting the pool address contract slot data at a specific block and copying all relevent data into the `static_pool_data_testing.csv`. By way of example, updating a uniswap_v3 type pool requires; a) setting the token balances of the two reserve tokens, b) setting the `liquidity` parameter on slot 4, and c) setting the entire slot 0 which includes the parameters `tick` and  `sqrtPriceX96`.
    - Slot information for contract parameters can be found at:
    
    https://evm.storage/eth/{blockNumber}/{pool_address}/{parameter_name}#map
    
    eg https://evm.storage/eth/19104620/0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8/liquidity#map

1) An instance of the arb bot is then initialized as a background process for the relevant `blockchain` and `mode` to be tested. 
1) Create the Carbon test strategies noting the `strategyid` assigned to each strategy
1) Verify the test data:
    - First by checking that all the created strategies have been traded against
    - Second by extracting the successful txhash files from the logs and matching their content exactly to the test results
1) The bot is then shutdown

## Suggested Improvements
1) Notebook should be converted to python file
1) Click options should be added for:
    - new/existing fork
    - blockchain
    - arb_mode