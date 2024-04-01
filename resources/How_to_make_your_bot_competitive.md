# How to Make your Bot more Competitive

## Overview

Typically only one bot-operator is able to close each arbitrage opportunity, making bot operation competitive in nature. The purpose of this document is to provide ideas on ways to improve your own bot. 

### Data Throughput
Faster data means faster cycles for the arbitrage bot. The easiest way to achieve this is by using a premium plan from a data provider such as Alchemy. 

Another way to achieve this is by running an Ethereum node locally. The bot can be connected to a local Ethereum node fairly easily by changing the RPC_URL in the fastlane_bot/config/providers file. Note that some functions require an Alchemy API key, making Alchemy necessary unless the functions themselves are modified. These functions are in fastlane_bot/helpers/txhelpers.

### New Arbitrage Modes
Currently the bot is geared towards closing pariwise & triangular arbitrage on Bancor V3 & Carbon, but it can easily be generalized for all the exchanges it supports. To do this, you would need to create a new Arb Mode file, and design the combinations that are fed into the Optimizer. A lot of the heavy lifting here is already handled, but there may be a few specific changes you would need to make to get it to work.





