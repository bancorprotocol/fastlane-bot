# How to Make your Bot more Competitive

## Overview

Typically only one bot-operator is able to close each arbitrage opportunity, making bot operation competitive in nature. The purpose of this document is to provide ideas on ways to improve your own bot. 

### Gas Priority Fee Optimization
In config/network.py there is a constant: DEFAULT_GAS_PRICE_OFFSET. This is a multiplier that increases the priority fee paid by your TX. The higher it is, the more likely your TX will get executed, but the more the TX costs. It’s set to increase by 9% by default, which is likely insufficient to be competitive. You could also design a custom function to modify the priority fee based on profit - this could likely make you competitive, but would require some work. 

### Data Throughput
Faster data means faster cycles for the arbitrage bot. The easiest way to achieve this is by using a premium plan from a data provider such as Alchemy. 

Another way to achieve this is by running an Ethereum node locally. The bot can be connected to a local Ethereum node fairly easily by changing the RPC_URL in the fastlane_bot/config/providers file. Note that some functions require an Alchemy API key, making Alchemy necessary unless the functions themselves are modified. 

These functions are in fastlane_bot/helpers/txhelpers, and include: 
* **get_access_list:** this function is optional - using it saves around 5000 gas on average per transaction.
* **submit_private_transaction:** this function is not optional, however it's possible to submit transactions directly to Flashbots. See the Flashbots Documentation for more details: https://docs.flashbots.net/flashbots-auction/advanced/rpc-endpoint
* **get_max_priority_fee_per_gas_alchemy:** this function is not optional, but could be replaced with custom priority fee logic. 

### New Arbitrage Modes
Currently the bot is geared towards closing pariwise & triangular arbitrage on Bancor V3 & Carbon, but it can easily be generalized for all the exchanges it supports. To do this, you would need to create a new Arb Mode file, and design the combinations that are fed into the Optimizer. A lot of the heavy lifting here is already handled, but there may be a few specific changes you would need to make to get it to work.





