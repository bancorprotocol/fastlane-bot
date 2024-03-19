"""
ABI's for the contracts used in the FastLane project

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""

FAST_LANE_CONTRACT_ABI = [
    {
        "type": "event",
        "name": "ArbitrageExecuted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "caller", "type": "address"}, {"indexed": False, "internalType": "uint16[]", "name": "platformIds", "type": "uint16[]"}, {"indexed": False, "internalType": "address[]", "name": "tokenPath", "type": "address[]"}, {"indexed": False, "internalType": "address[]", "name": "sourceTokens", "type": "address[]"}, {"indexed": False, "internalType": "uint256[]", "name": "sourceAmounts", "type": "uint256[]"}, {"indexed": False, "internalType": "uint256[]", "name": "protocolAmounts", "type": "uint256[]"}, {"indexed": False, "internalType": "uint256[]", "name": "rewardAmounts", "type": "uint256[]"}]
    },
    {
        "type": "event",
        "name": "Initialized",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "RewardsUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevPercentagePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newPercentagePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint256", "name": "prevMaxAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "newMaxAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}]
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "function",
        "name": "flashloanAndArbV2",
        "stateMutability": "nonpayable",
        "inputs": [{"components": [{"internalType": "uint16", "name": "platformId", "type": "uint16"}, {"internalType": "contract IERC20[]", "name": "sourceTokens", "type": "address[]"}, {"internalType": "uint256[]", "name": "sourceAmounts", "type": "uint256[]"}], "internalType": "struct BancorArbitrage.Flashloan[]", "name": "flashloans", "type": "tuple[]"}, {"components": [{"internalType": "uint16", "name": "platformId", "type": "uint16"}, {"internalType": "contract Token", "name": "sourceToken", "type": "address"}, {"internalType": "contract Token", "name": "targetToken", "type": "address"}, {"internalType": "uint256", "name": "sourceAmount", "type": "uint256"}, {"internalType": "uint256", "name": "minTargetAmount", "type": "uint256"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}, {"internalType": "address", "name": "customAddress", "type": "address"}, {"internalType": "uint256", "name": "customInt", "type": "uint256"}, {"internalType": "bytes", "name": "customData", "type": "bytes"}], "internalType": "struct BancorArbitrage.TradeRoute[]", "name": "routes", "type": "tuple[]"}],
        "outputs": []
    },
    {
        "type": "function",
        "name": "fundAndArb",
        "stateMutability": "payable",
        "inputs": [{"components": [{"internalType": "uint16", "name": "platformId", "type": "uint16"}, {"internalType": "contract Token", "name": "sourceToken", "type": "address"}, {"internalType": "contract Token", "name": "targetToken", "type": "address"}, {"internalType": "uint256", "name": "sourceAmount", "type": "uint256"}, {"internalType": "uint256", "name": "minTargetAmount", "type": "uint256"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}, {"internalType": "address", "name": "customAddress", "type": "address"}, {"internalType": "uint256", "name": "customInt", "type": "uint256"}, {"internalType": "bytes", "name": "customData", "type": "bytes"}], "internalType": "struct BancorArbitrage.TradeRoute[]", "name": "routes", "type": "tuple[]"}, {"internalType": "contract Token", "name": "token", "type": "address"}, {"internalType": "uint256", "name": "sourceAmount", "type": "uint256"}],
        "outputs": []
    },
    {
        "type": "function",
        "name": "rewards",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"components": [{"internalType": "uint32", "name": "percentagePPM", "type": "uint32"}, {"internalType": "uint256", "name": "maxAmount", "type": "uint256"}], "internalType": "struct BancorArbitrage.Rewards", "name": "", "type": "tuple"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

ERC20_ABI = [
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "guy", "type": "address"}, {"name": "wad", "type": "uint256"}],
        "outputs": [{"name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "fastlane_bot", "type": "address"}, {"indexed": True, "name": "guy", "type": "address"}, {"indexed": False, "name": "wad", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "fastlane_bot", "type": "address"}, {"indexed": True, "name": "dst", "type": "address"}, {"indexed": False, "name": "wad", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Deposit",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "dst", "type": "address"}, {"indexed": False, "name": "wad", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Withdrawal",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "fastlane_bot", "type": "address"}, {"indexed": False, "name": "wad", "type": "uint256"}]
    }
]

CARBON_CONTROLLER_ABI = [
    {
        "type": "event",
        "name": "AdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "previousAdmin", "type": "address"}, {"indexed": False, "internalType": "address", "name": "newAdmin", "type": "address"}]
    },
    {
        "type": "event",
        "name": "BeaconUpgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "beacon", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Upgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "implementation", "type": "address"}]
    },
    {
        "type": "event",
        "name": "FeesWithdrawn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "Token", "name": "token", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "uint256", "name": "amount", "type": "uint256"}, {"indexed": False, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Initialized",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint128", "name": "pairId", "type": "uint128"}, {"indexed": True, "internalType": "Token", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token1", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PairTradingFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "Token", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "Paused",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "account", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}]
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "StrategyCreated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token1", "type": "address"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "indexed": False, "internalType": "struct Order", "name": "order0", "type": "tuple"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "indexed": False, "internalType": "struct Order", "name": "order1", "type": "tuple"}]
    },
    {
        "type": "event",
        "name": "StrategyDeleted",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token1", "type": "address"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "indexed": False, "internalType": "struct Order", "name": "order0", "type": "tuple"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "indexed": False, "internalType": "struct Order", "name": "order1", "type": "tuple"}]
    },
    {
        "type": "event",
        "name": "StrategyUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint256", "name": "id", "type": "uint256"}, {"indexed": True, "internalType": "Token", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token1", "type": "address"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "indexed": False, "internalType": "struct Order", "name": "order0", "type": "tuple"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "indexed": False, "internalType": "struct Order", "name": "order1", "type": "tuple"}, {"indexed": False, "internalType": "uint8", "name": "reason", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "TokensTraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "trader", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "sourceToken", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "targetToken", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "sourceAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "targetAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint128", "name": "tradingFeeAmount", "type": "uint128"}, {"indexed": False, "internalType": "bool", "name": "byTargetAmount", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "TradingFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "Unpaused",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "account", "type": "address"}]
    },
    {
        "type": "function",
        "name": "pairTradingFeePPM",
        "stateMutability": "view",
        "inputs": [{"internalType": "Token", "name": "token0", "type": "address"}, {"internalType": "Token", "name": "token1", "type": "address"}],
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "pairs",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "Token[2][]", "name": "", "type": "address[2][]"}]
    },
    {
        "type": "function",
        "name": "strategiesByPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "Token", "name": "token0", "type": "address"}, {"internalType": "Token", "name": "token1", "type": "address"}, {"internalType": "uint256", "name": "startIndex", "type": "uint256"}, {"internalType": "uint256", "name": "endIndex", "type": "uint256"}],
        "outputs": [{"components": [{"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "Token[2]", "name": "tokens", "type": "address[2]"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "internalType": "struct Order[2]", "name": "orders", "type": "tuple[2]"}], "internalType": "struct Strategy[]", "name": "", "type": "tuple[]"}]
    },
    {
        "type": "function",
        "name": "strategy",
        "stateMutability": "view",
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "outputs": [{"components": [{"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "Token[2]", "name": "tokens", "type": "address[2]"}, {"components": [{"internalType": "uint128", "name": "y", "type": "uint128"}, {"internalType": "uint128", "name": "z", "type": "uint128"}, {"internalType": "uint64", "name": "A", "type": "uint64"}, {"internalType": "uint64", "name": "B", "type": "uint64"}], "internalType": "struct Order[2]", "name": "orders", "type": "tuple[2]"}], "internalType": "struct Strategy", "name": "", "type": "tuple"}]
    },
    {
        "type": "function",
        "name": "tradingFeePPM",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

SUSHISWAP_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "tkn0_address", "type": "address"}, {"indexed": True, "internalType": "address", "name": "tkn1_address", "type": "address"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

SUSHISWAP_ROUTER_ABI = [
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

SUSHISWAP_POOLS_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount0Out", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1Out", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint112", "name": "reserve0", "type": "uint112"}, {"indexed": False, "internalType": "uint112", "name": "reserve1", "type": "uint112"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getReserves",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint112", "name": "_reserve0", "type": "uint112"}, {"internalType": "uint112", "name": "_reserve1", "type": "uint112"}, {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

UNISWAP_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "tkn0_address", "type": "address"}, {"indexed": True, "internalType": "address", "name": "tkn1_address", "type": "address"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

ALIENBASE_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

PANCAKESWAP_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

PANCAKESWAP_V3_FACTORY_ABI = [
    {
        "type": "event",
        "name": "FeeAmountEnabled",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": True, "internalType": "int24", "name": "tickSpacing", "type": "int24"}]
    },
    {
        "type": "event",
        "name": "FeeAmountExtraInfoUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": False, "internalType": "bool", "name": "whitelistRequested", "type": "bool"}, {"indexed": False, "internalType": "bool", "name": "enabled", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "OwnerChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "oldOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"}, {"indexed": False, "internalType": "address", "name": "pool", "type": "address"}]
    },
    {
        "type": "event",
        "name": "SetLmPoolDeployer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "lmPoolDeployer", "type": "address"}]
    },
    {
        "type": "event",
        "name": "WhiteListAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "user", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "verified", "type": "bool"}]
    }
]

UNISWAP_V2_ROUTER_ABI = [
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

UNISWAP_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount0Out", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1Out", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint112", "name": "reserve0", "type": "uint112"}, {"indexed": False, "internalType": "uint112", "name": "reserve1", "type": "uint112"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getReserves",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint112", "name": "_reserve0", "type": "uint112"}, {"internalType": "uint112", "name": "_reserve1", "type": "uint112"}, {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

PANCAKESWAP_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount0Out", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1Out", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint112", "name": "reserve0", "type": "uint112"}, {"indexed": False, "internalType": "uint112", "name": "reserve1", "type": "uint112"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getReserves",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint112", "name": "_reserve0", "type": "uint112"}, {"internalType": "uint112", "name": "_reserve1", "type": "uint112"}, {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

PANCAKESWAP_V3_POOL_ABI = [
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount", "type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Collect",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount0", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "amount1", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "CollectProtocol",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint128", "name": "amount0", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "amount1", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "Flash",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "paid0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "paid1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "IncreaseObservationCardinalityNext",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint16", "name": "observationCardinalityNextOld", "type": "uint16"}, {"indexed": False, "internalType": "uint16", "name": "observationCardinalityNextNew", "type": "uint16"}]
    },
    {
        "type": "event",
        "name": "Initialize",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount", "type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "SetFeeProtocol",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "feeProtocol0Old", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "feeProtocol1Old", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "feeProtocol0New", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "feeProtocol1New", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "SetLmPoolEvent",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "addr", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "int256", "name": "amount0", "type": "int256"}, {"indexed": False, "internalType": "int256", "name": "amount1", "type": "int256"}, {"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "internalType": "uint128", "name": "liquidity", "type": "uint128"}, {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "protocolFeesToken0", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "protocolFeesToken1", "type": "uint128"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "fee",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint24", "name": "", "type": "uint24"}]
    },
    {
        "type": "function",
        "name": "liquidity",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}]
    },
    {
        "type": "function",
        "name": "slot0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"internalType": "int24", "name": "tick", "type": "int24"}, {"internalType": "uint16", "name": "observationIndex", "type": "uint16"}, {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"}, {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"}, {"internalType": "uint32", "name": "feeProtocol", "type": "uint32"}, {"internalType": "bool", "name": "unlocked", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "tickSpacing",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "int24", "name": "", "type": "int24"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

UNISWAP_V3_FACTORY_ABI = [
    {
        "type": "event",
        "name": "FeeAmountEnabled",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": True, "internalType": "int24", "name": "tickSpacing", "type": "int24"}]
    },
    {
        "type": "event",
        "name": "OwnerChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "oldOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "tkn0_address", "type": "address"}, {"indexed": True, "internalType": "address", "name": "tkn1_address", "type": "address"}, {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"}, {"indexed": False, "internalType": "address", "name": "pool", "type": "address"}]
    }
]

UNISWAP_V3_POOL_ABI = [
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount", "type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Collect",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount0", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "amount1", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "CollectProtocol",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint128", "name": "amount0", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "amount1", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "Flash",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "paid0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "paid1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "IncreaseObservationCardinalityNext",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint16", "name": "observationCardinalityNextOld", "type": "uint16"}, {"indexed": False, "internalType": "uint16", "name": "observationCardinalityNextNew", "type": "uint16"}]
    },
    {
        "type": "event",
        "name": "Initialize",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount", "type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "SetFeeProtocol",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint8", "name": "feeProtocol0Old", "type": "uint8"}, {"indexed": False, "internalType": "uint8", "name": "feeProtocol1Old", "type": "uint8"}, {"indexed": False, "internalType": "uint8", "name": "feeProtocol0New", "type": "uint8"}, {"indexed": False, "internalType": "uint8", "name": "feeProtocol1New", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "int256", "name": "amount0", "type": "int256"}, {"indexed": False, "internalType": "int256", "name": "amount1", "type": "int256"}, {"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "internalType": "uint128", "name": "liquidity", "type": "uint128"}, {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "fee",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint24", "name": "", "type": "uint24"}]
    },
    {
        "type": "function",
        "name": "liquidity",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}]
    },
    {
        "type": "function",
        "name": "slot0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"internalType": "int24", "name": "tick", "type": "int24"}, {"internalType": "uint16", "name": "observationIndex", "type": "uint16"}, {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"}, {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"}, {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"}, {"internalType": "bool", "name": "unlocked", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "tickSpacing",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "int24", "name": "", "type": "int24"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

UNISWAP_V3_ROUTER_ABI = [
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

UNISWAP_V3_ROUTER2_ABI = [
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

BANCOR_NETWORK_ABI = [
    {
        "type": "event",
        "name": "AdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "previousAdmin", "type": "address"}, {"indexed": False, "internalType": "address", "name": "newAdmin", "type": "address"}]
    },
    {
        "type": "event",
        "name": "BeaconUpgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "beacon", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Upgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "implementation", "type": "address"}]
    }
]

BANCOR_V3_NETWORK_INFO_ABI = [
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}]
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "function",
        "name": "tradingFeePPM",
        "stateMutability": "view",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "tradingLiquidity",
        "stateMutability": "view",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"components": [{"internalType": "uint128", "name": "bntTradingLiquidity", "type": "uint128"}, {"internalType": "uint128", "name": "baseTokenTradingLiquidity", "type": "uint128"}], "internalType": "struct TradingLiquidity", "name": "", "type": "tuple"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

BANCOR_V2_ROUTER_ABI = [
    {
        "type": "event",
        "name": "Conversion",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "_smartToken", "type": "address"}, {"indexed": True, "name": "_fromToken", "type": "address"}, {"indexed": True, "name": "_toToken", "type": "address"}, {"indexed": False, "name": "_fromAmount", "type": "uint256"}, {"indexed": False, "name": "_toAmount", "type": "uint256"}, {"indexed": False, "name": "_trader", "type": "address"}]
    },
    {
        "type": "event",
        "name": "OwnerUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "_prevOwner", "type": "address"}, {"indexed": True, "name": "_newOwner", "type": "address"}]
    }
]

BANCOR_V2_CONVERTER_ABI = [
    {
        "type": "event",
        "name": "Activation",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint16", "name": "_type", "type": "uint16"}, {"indexed": True, "internalType": "contract IConverterAnchor", "name": "_anchor", "type": "address"}, {"indexed": True, "internalType": "bool", "name": "_activated", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "Conversion",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IERC20", "name": "_fromToken", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "_toToken", "type": "address"}, {"indexed": True, "internalType": "address", "name": "_trader", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "_amount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "_return", "type": "uint256"}, {"indexed": False, "internalType": "int256", "name": "_conversionFee", "type": "int256"}]
    },
    {
        "type": "event",
        "name": "ConversionFeeUpdate",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "_prevFee", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "_newFee", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "LiquidityAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_provider", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "_reserveToken", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "_amount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "_newBalance", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "_newSupply", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "LiquidityRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_provider", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "_reserveToken", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "_amount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "_newBalance", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "_newSupply", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "OwnerUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_prevOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "_newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokenRateUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IERC20", "name": "_token1", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "_token2", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "_rateN", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "_rateD", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "anchor",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "contract IConverterAnchor", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "connectorTokens",
        "stateMutability": "view",
        "inputs": [{"internalType": "uint256", "name": "_index", "type": "uint256"}],
        "outputs": [{"internalType": "contract IERC20", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "conversionFee",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "reserveBalances",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}, {"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "reserveTokens",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "contract IERC20[]", "name": "", "type": "address[]"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

BANCOR_V2_CONTRACT_REGISTRY_ABI = [
    {
        "type": "event",
        "name": "AddressUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "_contractName", "type": "bytes32"}, {"indexed": False, "name": "_contractAddress", "type": "address"}]
    },
    {
        "type": "event",
        "name": "OwnerUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "_prevOwner", "type": "address"}, {"indexed": True, "name": "_newOwner", "type": "address"}]
    }
]

BANCOR_V2_CONVERTER_REGISTRY_ABI = [
    {
        "type": "event",
        "name": "ConverterAnchorAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IConverterAnchor", "name": "_anchor", "type": "address"}]
    },
    {
        "type": "event",
        "name": "ConverterAnchorRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IConverterAnchor", "name": "_anchor", "type": "address"}]
    },
    {
        "type": "event",
        "name": "ConvertibleTokenAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IERC20Token", "name": "_convertibleToken", "type": "address"}, {"indexed": True, "internalType": "contract IConverterAnchor", "name": "_smartToken", "type": "address"}]
    },
    {
        "type": "event",
        "name": "ConvertibleTokenRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IERC20Token", "name": "_convertibleToken", "type": "address"}, {"indexed": True, "internalType": "contract IConverterAnchor", "name": "_smartToken", "type": "address"}]
    },
    {
        "type": "event",
        "name": "LiquidityPoolAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IConverterAnchor", "name": "_liquidityPool", "type": "address"}]
    },
    {
        "type": "event",
        "name": "LiquidityPoolRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IConverterAnchor", "name": "_liquidityPool", "type": "address"}]
    },
    {
        "type": "event",
        "name": "OwnerUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_prevOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "_newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "SmartTokenAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IConverterAnchor", "name": "_smartToken", "type": "address"}]
    },
    {
        "type": "event",
        "name": "SmartTokenRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IConverterAnchor", "name": "_smartToken", "type": "address"}]
    }
]

BANCOR_V2_POOL_TOKEN_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "_spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "_value", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Destruction",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "_amount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Issuance",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "_amount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "OwnerUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_prevOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "_newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "_from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "_to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "_value", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "_spender", "type": "address"}, {"internalType": "uint256", "name": "_value", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    }
]

BANCOR_V3_NETWORK_ABI = [
    {
        "type": "event",
        "name": "AdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "previousAdmin", "type": "address"}, {"indexed": False, "internalType": "address", "name": "newAdmin", "type": "address"}]
    },
    {
        "type": "event",
        "name": "BeaconUpgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "beacon", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Upgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "implementation", "type": "address"}]
    },
    {
        "type": "event",
        "name": "FlashLoanCompleted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "token", "type": "address"}, {"indexed": True, "internalType": "address", "name": "borrower", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "feeAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "FundsMigrated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "contract Token", "name": "token", "type": "address"}, {"indexed": True, "internalType": "address", "name": "provider", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "availableAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "originalAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "NetworkFeesWithdrawn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "caller", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "POLRewardsPPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "oldRewardsPPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newRewardsPPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "POLWithdrawn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "caller", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "polTokenAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "userReward", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Paused",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "account", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "contract IPoolCollection", "name": "poolCollection", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolCollectionAdded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint16", "name": "poolType", "type": "uint16"}, {"indexed": True, "internalType": "contract IPoolCollection", "name": "poolCollection", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolCollectionRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint16", "name": "poolType", "type": "uint16"}, {"indexed": True, "internalType": "contract IPoolCollection", "name": "poolCollection", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "contract IPoolCollection", "name": "poolCollection", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PoolRemoved",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "contract IPoolCollection", "name": "poolCollection", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}]
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokensTraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "contract Token", "name": "sourceToken", "type": "address"}, {"indexed": True, "internalType": "contract Token", "name": "targetToken", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "sourceAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "targetAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "bntAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "targetFeeAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "bntFeeAmount", "type": "uint256"}, {"indexed": False, "internalType": "address", "name": "trader", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Unpaused",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "account", "type": "address"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    },
    {
        "type": "function",
        "name": "withdrawPOL",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

BANCOR_V3_POOL_COLLECTION_ABI = [
    {
        "type": "event",
        "name": "DefaultTradingFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "DepositingEnabled",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "bool", "name": "newStatus", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "NetworkFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "OwnerUpdate",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "prevOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokensDeposited",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "provider", "type": "address"}, {"indexed": True, "internalType": "contract Token", "name": "tkn_address", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "baseTokenAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "poolTokenAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "TokensWithdrawn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "provider", "type": "address"}, {"indexed": True, "internalType": "contract Token", "name": "tkn_address", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "baseTokenAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "poolTokenAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "externalProtectionBaseTokenAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "bntAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "withdrawalFeeAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "TotalLiquidityUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "liquidity", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "stakedBalance", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "poolTokenSupply", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "TradingEnabled",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "bool", "name": "newStatus", "type": "bool"}, {"indexed": True, "internalType": "uint8", "name": "reason", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "TradingFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "TradingLiquidityUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "contract Token", "name": "tkn_address", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "prevLiquidity", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "newLiquidity", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "poolData",
        "stateMutability": "view",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"components": [{"internalType": "contract IPoolToken", "name": "poolToken", "type": "address"}, {"internalType": "uint32", "name": "tradingFeePPM", "type": "uint32"}, {"internalType": "bool", "name": "tradingEnabled", "type": "bool"}, {"internalType": "bool", "name": "depositingEnabled", "type": "bool"}, {"components": [{"internalType": "uint32", "name": "blockNumber", "type": "uint32"}, {"components": [{"internalType": "uint112", "name": "n", "type": "uint112"}, {"internalType": "uint112", "name": "d", "type": "uint112"}], "internalType": "struct Fraction112", "name": "rate", "type": "tuple"}, {"components": [{"internalType": "uint112", "name": "n", "type": "uint112"}, {"internalType": "uint112", "name": "d", "type": "uint112"}], "internalType": "struct Fraction112", "name": "invRate", "type": "tuple"}], "internalType": "struct AverageRates", "name": "averageRates", "type": "tuple"}, {"components": [{"internalType": "uint128", "name": "bntTradingLiquidity", "type": "uint128"}, {"internalType": "uint128", "name": "baseTokenTradingLiquidity", "type": "uint128"}, {"internalType": "uint256", "name": "stakedBalance", "type": "uint256"}], "internalType": "struct PoolLiquidity", "name": "liquidity", "type": "tuple"}], "internalType": "struct Pool", "name": "", "type": "tuple"}]
    },
    {
        "type": "function",
        "name": "tradingFeePPM",
        "stateMutability": "view",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

BANCOR_POL_ABI = [
    {
        "type": "event",
        "name": "AdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "previousAdmin", "type": "address"}, {"indexed": False, "internalType": "address", "name": "newAdmin", "type": "address"}]
    },
    {
        "type": "event",
        "name": "BeaconUpgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "beacon", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Upgraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "implementation", "type": "address"}]
    },
    {
        "type": "event",
        "name": "EthSaleAmountUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint128", "name": "prevEthSaleAmount", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "newEthSaleAmount", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "Initialized",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "MarketPriceMultiplyUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevMarketPriceMultiply", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newMarketPriceMultiply", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "MinEthSaleAmountUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint128", "name": "prevMinEthSaleAmount", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "newMinEthSaleAmount", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "PriceDecayHalfLifeUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevPriceDecayHalfLife", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newPriceDecayHalfLife", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "PriceUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "Token", "name": "token", "type": "address"}, {"components": [{"internalType": "uint128", "name": "sourceAmount", "type": "uint128"}, {"internalType": "uint128", "name": "targetAmount", "type": "uint128"}], "indexed": False, "internalType": "struct ICarbonPOL.Price", "name": "price", "type": "tuple"}]
    },
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}]
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokenTraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "caller", "type": "address"}, {"indexed": True, "internalType": "Token", "name": "token", "type": "address"}, {"indexed": False, "internalType": "uint128", "name": "inputAmount", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "outputAmount", "type": "uint128"}]
    },
    {
        "type": "event",
        "name": "TradingEnabled",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "Token", "name": "token", "type": "address"}, {"components": [{"internalType": "uint128", "name": "sourceAmount", "type": "uint128"}, {"internalType": "uint128", "name": "targetAmount", "type": "uint128"}], "indexed": False, "internalType": "struct ICarbonPOL.Price", "name": "price", "type": "tuple"}]
    },
    {
        "type": "function",
        "name": "amountAvailableForTrading",
        "stateMutability": "view",
        "inputs": [{"internalType": "Token", "name": "token", "type": "address"}],
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}]
    },
    {
        "type": "function",
        "name": "tokenPrice",
        "stateMutability": "view",
        "inputs": [{"internalType": "Token", "name": "token", "type": "address"}],
        "outputs": [{"components": [{"internalType": "uint128", "name": "sourceAmount", "type": "uint128"}, {"internalType": "uint128", "name": "targetAmount", "type": "uint128"}], "internalType": "struct ICarbonPOL.Price", "name": "", "type": "tuple"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

BANCOR_V3_NETWORK_SETTINGS = [
    {
        "type": "event",
        "name": "DefaultFlashLoanFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "FlashLoanFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "event",
        "name": "FundingLimitUpdated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "prevLimit", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "newLimit", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "MinLiquidityForTradingUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "prevLiquidity", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "newLiquidity", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "newAdminRole", "type": "bytes32"}]
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "account", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokenAddedToWhitelist",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "token", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokenAddedToWhitelistForPOL",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "token", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokenRemovedFromWhitelist",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "token", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokenRemovedFromWhitelistForPOL",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "token", "type": "address"}]
    },
    {
        "type": "event",
        "name": "VortexBurnRewardUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevBurnRewardPPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newBurnRewardPPM", "type": "uint32"}, {"indexed": False, "internalType": "uint256", "name": "prevBurnRewardMaxAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "newBurnRewardMaxAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "WithdrawalFeePPMUpdated",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint32", "name": "prevFeePPM", "type": "uint32"}, {"indexed": False, "internalType": "uint32", "name": "newFeePPM", "type": "uint32"}]
    },
    {
        "type": "function",
        "name": "tokenWhitelistForPOL",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "contract Token[]", "name": "", "type": "address[]"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}]
    }
]

MULTICALL_ABI = [
    {
        "type": "function",
        "name": "aggregate",
        "stateMutability": "view",
        "inputs": [{"components": [{"internalType": "address", "name": "target", "type": "address"}, {"internalType": "bytes", "name": "callData", "type": "bytes"}], "internalType": "struct Multicall2.Call[]", "name": "calls", "type": "tuple[]"}],
        "outputs": [{"internalType": "uint256", "name": "blockNumber", "type": "uint256"}, {"internalType": "bytes[]", "name": "returnData", "type": "bytes[]"}]
    }
]

BALANCER_VAULT_ABI = [
    {
        "type": "event",
        "name": "AuthorizerChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IAuthorizer", "name": "newAuthorizer", "type": "address"}]
    },
    {
        "type": "event",
        "name": "ExternalBalanceTransfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IERC20", "name": "token", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "FlashLoan",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract IFlashLoanRecipient", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "token", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "feeAmount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "InternalBalanceChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "user", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "token", "type": "address"}, {"indexed": False, "internalType": "int256", "name": "delta", "type": "int256"}]
    },
    {
        "type": "event",
        "name": "PausedStateChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "bool", "name": "paused", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "PoolBalanceChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "poolId", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "liquidityProvider", "type": "address"}, {"indexed": False, "internalType": "contract IERC20[]", "name": "tokens", "type": "address[]"}, {"indexed": False, "internalType": "int256[]", "name": "deltas", "type": "int256[]"}, {"indexed": False, "internalType": "uint256[]", "name": "protocolFeeAmounts", "type": "uint256[]"}]
    },
    {
        "type": "event",
        "name": "PoolBalanceManaged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "poolId", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "assetManager", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "token", "type": "address"}, {"indexed": False, "internalType": "int256", "name": "cashDelta", "type": "int256"}, {"indexed": False, "internalType": "int256", "name": "managedDelta", "type": "int256"}]
    },
    {
        "type": "event",
        "name": "PoolRegistered",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "poolId", "type": "bytes32"}, {"indexed": True, "internalType": "address", "name": "poolAddress", "type": "address"}, {"indexed": False, "internalType": "enum IVault.PoolSpecialization", "name": "specialization", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "RelayerApprovalChanged",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "relayer", "type": "address"}, {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "approved", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "poolId", "type": "bytes32"}, {"indexed": True, "internalType": "contract IERC20", "name": "tokenIn", "type": "address"}, {"indexed": True, "internalType": "contract IERC20", "name": "tokenOut", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amountIn", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amountOut", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "TokensDeregistered",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "poolId", "type": "bytes32"}, {"indexed": False, "internalType": "contract IERC20[]", "name": "tokens", "type": "address[]"}]
    },
    {
        "type": "event",
        "name": "TokensRegistered",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "poolId", "type": "bytes32"}, {"indexed": False, "internalType": "contract IERC20[]", "name": "tokens", "type": "address[]"}, {"indexed": False, "internalType": "address[]", "name": "assetManagers", "type": "address[]"}]
    },
    {
        "type": "function",
        "name": "getPoolTokens",
        "stateMutability": "view",
        "inputs": [{"internalType": "bytes32", "name": "poolId", "type": "bytes32"}],
        "outputs": [{"internalType": "contract IERC20[]", "name": "tokens", "type": "address[]"}, {"internalType": "uint256[]", "name": "balances", "type": "uint256[]"}, {"internalType": "uint256", "name": "lastChangeBlock", "type": "uint256"}]
    }
]

BALANCER_POOL_ABI_V1 = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "OracleEnabledChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "bool", "name": "enabled", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "PausedStateChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "bool", "name": "paused", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "SwapFeePercentageChanged",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "swapFeePercentage", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "pure",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "getSwapFeePercentage",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    }
]

SOLIDLY_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": True, "internalType": "bool", "name": "stable", "type": "bool"}, {"indexed": False, "internalType": "address", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "SetCustomFee",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "fee", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "SetFeeManager",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "feeManager", "type": "address"}]
    },
    {
        "type": "event",
        "name": "SetPauseState",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "bool", "name": "state", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "SetPauser",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "pauser", "type": "address"}]
    },
    {
        "type": "event",
        "name": "SetVoter",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "address", "name": "voter", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"}, {"internalType": "bool", "name": "_stable", "type": "bool"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "voter",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

SOLIDLY_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Claim",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "EIP712DomainChanged",
        "anonymous": False,
        "inputs": []
    },
    {
        "type": "event",
        "name": "Fees",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount0Out", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1Out", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "reserve0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "reserve1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getReserves",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "_reserve0", "type": "uint256"}, {"internalType": "uint256", "name": "_reserve1", "type": "uint256"}, {"internalType": "uint256", "name": "_blockTimestampLast", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "stable",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

EQUALIZER_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Claim",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Fees",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Initialized",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount0Out", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1Out", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "reserve0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "reserve1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "factory",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getReserves",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "_reserve0", "type": "uint256"}, {"internalType": "uint256", "name": "_reserve1", "type": "uint256"}, {"internalType": "uint256", "name": "_blockTimestampLast", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "stable",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

VELOCIMETER_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Approval",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Burn",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "ExternalBribeSet",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "externalBribe", "type": "address"}]
    },
    {
        "type": "event",
        "name": "GaugeFees",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}, {"indexed": False, "internalType": "address", "name": "externalBribe", "type": "address"}]
    },
    {
        "type": "event",
        "name": "HasGaugeSet",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "bool", "name": "value", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "Mint",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1In", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount0Out", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1Out", "type": "uint256"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "reserve0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "reserve1", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "TankFees",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}, {"indexed": False, "internalType": "address", "name": "tank", "type": "address"}]
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}]
    },
    {
        "type": "function",
        "name": "getReserves",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "_reserve0", "type": "uint256"}, {"internalType": "uint256", "name": "_reserve1", "type": "uint256"}, {"internalType": "uint256", "name": "_blockTimestampLast", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "stable",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    },
    {
        "type": "function",
        "name": "token0",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "token1",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "voter",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

VELOCIMETER_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "FeeSet",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "setter", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "stable", "type": "bool"}, {"indexed": False, "internalType": "uint256", "name": "fee", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "OwnershipTransferred",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}]
    },
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "stable", "type": "bool"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "event",
        "name": "Paused",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "pauser", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "paused", "type": "bool"}]
    },
    {
        "type": "event",
        "name": "TankSet",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "setter", "type": "address"}, {"indexed": True, "internalType": "address", "name": "tank", "type": "address"}]
    },
    {
        "type": "event",
        "name": "VoterSet",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "setter", "type": "address"}, {"indexed": True, "internalType": "address", "name": "voter", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "_pair", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "voter",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

SCALE_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "Initialized",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}]
    },
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "stable", "type": "bool"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "bool", "name": "_stable", "type": "bool"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getRealFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "_pair", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

GAS_ORACLE_ABI = [
    {
        "type": "function",
        "name": "basefee",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "l1FeeOverhead",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "l1FeeScalar",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "version",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "string", "name": "", "type": "string"}]
    }
]
