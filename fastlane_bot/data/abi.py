"""
ABI's for the EVM contracts interfaced

Contains the following ABI's:

- ``FAST_LANE_CONTRACT_ABI``: FastLane arbitrage contract
- ``ERC20_ABI``: generic ERC20 token contract
- ``SUSHISWAP_FACTORY_ABI``: Sushiswap factory contract
- ``SUSHISWAP_ROUTER_ABI``: Sushiswap router contract
- ``SUSHISWAP_POOLS_ABI``: Sushiswap pools contract
- other ABIs of exchanges we support

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""

FAST_LANE_CONTRACT_ABI = [
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
    }
]

ERC20_ABI = [
    {
        "type": "function",
        "name": "symbol",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "string"}]
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
        "inputs": [{"name": "owner", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "spender", "type": "address"}, {"name": "value", "type": "uint256"}],
        "outputs": [{"name": "", "type": "bool"}]
    }
]

CARBON_CONTROLLER_ABI = [
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
    }
]

UNISWAP_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

UNISWAP_V3_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"}, {"indexed": False, "internalType": "address", "name": "pool", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getPool",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}, {"internalType": "uint24", "name": "", "type": "uint24"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
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
        "type": "function",
        "name": "getFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"}, {"internalType": "bool", "name": "_stable", "type": "bool"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getPool",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "tokenA", "type": "address"}, {"internalType": "address", "name": "tokenB", "type": "address"}, {"internalType": "bool", "name": "stable", "type": "bool"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    }
]

VELOCIMETER_V2_FACTORY_ABI = [
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
        "inputs": [{"internalType": "address", "name": "_pair", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}, {"internalType": "bool", "name": "", "type": "bool"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

SCALE_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "stable", "type": "bool"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getRealFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "_pair", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}, {"internalType": "bool", "name": "", "type": "bool"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

CLEOPATRA_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"type": "address", "name": "token0", "internalType": "address", "indexed": True}, {"type": "address", "name": "token1", "internalType": "address", "indexed": True}, {"type": "bool", "name": "stable", "internalType": "bool", "indexed": False}, {"type": "address", "name": "pair", "internalType": "address", "indexed": False}, {"type": "uint256", "name": "", "internalType": "uint256", "indexed": False}]
    },
    {
        "type": "function",
        "name": "getPairFee",
        "stateMutability": "view",
        "inputs": [{"type": "address", "name": "_pair", "internalType": "address"}, {"type": "bool", "name": "_stable", "internalType": "bool"}],
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}]
    },
    {
        "type": "function",
        "name": "getPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}, {"internalType": "bool", "name": "", "type": "bool"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

LYNEX_V2_FACTORY_ABI = [
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
        "name": "getPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}, {"internalType": "bool", "name": "", "type": "bool"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

NILE_V2_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PairCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "stable", "type": "bool"}, {"indexed": False, "internalType": "address", "name": "pair", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "pairFee",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "_pool", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "fee", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getPair",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}, {"internalType": "bool", "name": "", "type": "bool"}],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

XFAI_V0_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token", "type": "address"}, {"indexed": True, "internalType": "address", "name": "pool", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "allPoolsSize", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getXfaiCore",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    },
    {
        "type": "function",
        "name": "getPool",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "_token", "type": "address"}],
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
    }
]

XFAI_V0_CORE_ABI = [
    {
        "type": "function",
        "name": "getTotalFee",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

UNISWAP_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint112", "name": "reserve0", "type": "uint112"}, {"indexed": False, "internalType": "uint112", "name": "reserve1", "type": "uint112"}]
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

UNISWAP_V3_POOL_ABI = [
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "int256", "name": "amount0", "type": "int256"}, {"indexed": False, "internalType": "int256", "name": "amount1", "type": "int256"}, {"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "internalType": "uint128", "name": "liquidity", "type": "uint128"}, {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"}]
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

PANCAKESWAP_V3_POOL_ABI = [
    {
        "type": "event",
        "name": "Swap",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": False, "internalType": "int256", "name": "amount0", "type": "int256"}, {"indexed": False, "internalType": "int256", "name": "amount1", "type": "int256"}, {"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}, {"indexed": False, "internalType": "uint128", "name": "liquidity", "type": "uint128"}, {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "protocolFeesToken0", "type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "protocolFeesToken1", "type": "uint128"}]
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

SOLIDLY_V2_POOL_ABI = [
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "reserve0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "reserve1", "type": "uint256"}]
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

XFAI_V0_POOL_ABI = [
    {
        "type": "event",
        "name": "Sync",
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "reserve0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "reserve1", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "getStates",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}, {"internalType": "uint256", "name": "", "type": "uint256"}]
    },
    {
        "type": "function",
        "name": "poolToken",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "address", "name": "", "type": "address"}]
    }
]

BANCOR_V2_CONVERTER_ABI = [
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
    }
]

BANCOR_V3_NETWORK_INFO_ABI = [
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
    }
]

BANCOR_V3_POOL_COLLECTION_ABI = [
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
        "name": "tradingFeePPM",
        "stateMutability": "view",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}]
    }
]

BANCOR_POL_ABI = [
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
        "type": "function",
        "name": "getPoolTokens",
        "stateMutability": "view",
        "inputs": [{"internalType": "bytes32", "name": "poolId", "type": "bytes32"}],
        "outputs": [{"internalType": "contract IERC20[]", "name": "tokens", "type": "address[]"}, {"internalType": "uint256[]", "name": "balances", "type": "uint256[]"}, {"internalType": "uint256", "name": "lastChangeBlock", "type": "uint256"}]
    }
]

BALANCER_POOL_ABI_V1 = [
    {
        "type": "function",
        "name": "getSwapFeePercentage",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

MULTICALL_ABI = [
    {
        "type": "function",
        "name": "tryAggregate",
        "stateMutability": "view",
        "inputs": [{"internalType": "bool", "name": "requireSuccess", "type": "bool"}, {"components": [{"internalType": "address", "name": "target", "type": "address"}, {"internalType": "bytes", "name": "callData", "type": "bytes"}], "internalType": "struct Multicall3.Call[]", "name": "calls", "type": "tuple[]"}],
        "outputs": [{"components": [{"internalType": "bool", "name": "success", "type": "bool"}, {"internalType": "bytes", "name": "returnData", "type": "bytes"}], "internalType": "struct Multicall3.Result[]", "name": "returnData", "type": "tuple[]"}]
    }
]

GAS_ORACLE_ABI = [
    {
        "type": "function",
        "name": "getL1Fee",
        "stateMutability": "view",
        "inputs": [{"internalType": "bytes", "name": "_data", "type": "bytes"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]
