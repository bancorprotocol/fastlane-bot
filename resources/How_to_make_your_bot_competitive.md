# How to Make your Bot more Competitive

## Overview

Typically only one bot-operator is able to close each arbitrage opportunity, making bot operation competitive in nature. The purpose of this document is to provide ideas on ways to improve your own bot. 

### Gas Fee Optimization
Function `gas_strategy` (in config/network.py) allows you to implement your own gas-strategy.
It takes a `Web3` instance as input, and it should return a dictionary specifying `maxFeePerGas` and `maxPriorityFeePerGas` as output.
By default, it returns the network's current values (obtained by sending `eth_gasPrice` and `eth_maxPriorityFeePerGas` requests to the node).
The tradeoff for each transaction is between the expected execution time and the expected profit.
Higher values generally reduce the expected execution time, but they also reduce the expected profit.

### Data Throughput
Faster data means faster cycles for the arbitrage bot. The easiest way to achieve this is by using a premium plan from a data provider such as Alchemy. 

Another way to achieve this is by running an Ethereum node locally. The bot can be connected to a local Ethereum node fairly easily by changing `self.RPC_URL` in file `fastlane_bot/config/provider.py`.

### New Arbitrage Modes
Currently the bot is geared towards closing pariwise & triangular arbitrage on Bancor V3 & Carbon, but it can easily be generalized for all the exchanges it supports. To do this, you would need to create a new Arb Mode file, and design the combinations that are fed into the Optimizer. A lot of the heavy lifting here is already handled, but there may be a few specific changes you would need to make to get it to work.





