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
    }
]

UNISWAP_V3_FACTORY_ABI = [
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "address", "name": "token0", "type": "address"}, {"indexed": True, "internalType": "address", "name": "token1", "type": "address"}, {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"}, {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"}, {"indexed": False, "internalType": "address", "name": "pool", "type": "address"}]
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
    }
]

PANCAKESWAP_V2_FACTORY_ABI = [{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"token0","type":"address"},{"indexed":True,"internalType":"address","name":"token1","type":"address"},{"indexed":False,"internalType":"address","name":"pair","type":"address"},{"indexed":False,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":True,"inputs":[],"name":"INIT_CODE_PAIR_HASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]

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

BANCOR_V3_NETWORK_ABI = [
    {
        "type": "event",
        "name": "PoolCreated",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "contract Token", "name": "pool", "type": "address"}, {"indexed": True, "internalType": "contract IPoolCollection", "name": "poolCollection", "type": "address"}]
    },
    {
        "type": "event",
        "name": "TokensTraded",
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "contextId", "type": "bytes32"}, {"indexed": True, "internalType": "contract Token", "name": "sourceToken", "type": "address"}, {"indexed": True, "internalType": "contract Token", "name": "targetToken", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "sourceAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "targetAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "bntAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "targetFeeAmount", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "bntFeeAmount", "type": "uint256"}, {"indexed": False, "internalType": "address", "name": "trader", "type": "address"}]
    },
    {
        "type": "function",
        "name": "withdrawPOL",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "contract Token", "name": "pool", "type": "address"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]

BANCOR_V3_NETWORK_SETTINGS = [
    {
        "type": "function",
        "name": "tokenWhitelistForPOL",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"internalType": "contract Token[]", "name": "", "type": "address[]"}]
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
        "name": "aggregate",
        "stateMutability": "view",
        "inputs": [{"components": [{"internalType": "address", "name": "target", "type": "address"}, {"internalType": "bytes", "name": "callData", "type": "bytes"}], "internalType": "struct Multicall2.Call[]", "name": "calls", "type": "tuple[]"}],
        "outputs": [{"internalType": "uint256", "name": "blockNumber", "type": "uint256"}, {"internalType": "bytes[]", "name": "returnData", "type": "bytes[]"}]
    }
]

VELOCORE_V2_FACTORY_ABI = [{"inputs":[{"internalType":"contract IVault","name":"vault_","type":"address"},{"internalType":"contract ConstantProductLibrary","name":"lib_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"uint256","name":"decay","type":"uint256","indexed":False}],"type":"event","name":"DecayChanged","anonymous":False},{"inputs":[{"internalType":"uint256","name":"fee1e18","type":"uint256","indexed":False}],"type":"event","name":"FeeChanged","anonymous":False},{"inputs":[{"internalType":"contract ConstantProductPool","name":"pool","type":"address","indexed":True},{"internalType":"Token","name":"t1","type":"bytes32","indexed":False},{"internalType":"Token","name":"t2","type":"bytes32","indexed":False}],"type":"event","name":"PoolCreated","anonymous":False},{"inputs":[{"internalType":"Token","name":"quoteToken","type":"bytes32"},{"internalType":"Token","name":"baseToken","type":"bytes32"}],"stateMutability":"nonpayable","type":"function","name":"deploy","outputs":[{"internalType":"contract ConstantProductPool","name":"","type":"address"}]},{"inputs":[{"internalType":"uint256","name":"begin","type":"uint256"},{"internalType":"uint256","name":"maxLength","type":"uint256"}],"stateMutability":"view","type":"function","name":"getPools","outputs":[{"internalType":"contract ConstantProductPool[]","name":"pools","type":"address[]"}]},{"inputs":[{"internalType":"contract ConstantProductPool","name":"","type":"address"}],"stateMutability":"view","type":"function","name":"isPool","outputs":[{"internalType":"bool","name":"","type":"bool"}]},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function","name":"poolList","outputs":[{"internalType":"contract ConstantProductPool","name":"","type":"address"}]},{"inputs":[{"internalType":"Token","name":"","type":"bytes32"},{"internalType":"Token","name":"","type":"bytes32"}],"stateMutability":"view","type":"function","name":"pools","outputs":[{"internalType":"contract ConstantProductPool","name":"","type":"address"}]},{"inputs":[],"stateMutability":"view","type":"function","name":"poolsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}]},{"inputs":[{"internalType":"uint32","name":"decay_","type":"uint32"}],"stateMutability":"nonpayable","type":"function","name":"setDecay"},{"inputs":[{"internalType":"uint32","name":"fee1e9_","type":"uint32"}],"stateMutability":"nonpayable","type":"function","name":"setFee"}]
                             
VELOCORE_V2_LENS_ABI = [{"inputs":[{"internalType":"Token","name":"usdc_","type":"bytes32"},{"internalType":"contract VC","name":"vc_","type":"address"},{"internalType":"contract ConstantProductPoolFactory","name":"factory_","type":"address"},{"internalType":"contract WombatRegistry","name":"wombatRegistry_","type":"address"},{"internalType":"contract VelocoreLens","name":"lens_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeAttached","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IConverter","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Convert","type":"event"},{"anonymous":False,"inputs":[{"components":[{"internalType":"address","name":"facetAddress","type":"address"},{"internalType":"enum VaultStorage.FacetCutAction","name":"action","type":"uint8"},{"internalType":"bytes4[]","name":"functionSelectors","type":"bytes4[]"}],"indexed":False,"internalType":"struct VaultStorage.FacetCut[]","name":"_diamondCut","type":"tuple[]"},{"indexed":False,"internalType":"address","name":"_init","type":"address"},{"indexed":False,"internalType":"bytes","name":"_calldata","type":"bytes"}],"name":"DiamondCut","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Gauge","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":False,"internalType":"bool","name":"killed","type":"bool"}],"name":"GaugeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract ISwap","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Swap","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"UserBalance","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"int256","name":"voteDelta","type":"int256"}],"name":"Vote","type":"event"},{"inputs":[],"name":"canonicalPoolLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"begin","type":"uint256"},{"internalType":"uint256","name":"maxLength","type":"uint256"}],"name":"canonicalPools","outputs":[{"components":[{"internalType":"address","name":"gauge","type":"address"},{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"poolData","type":"tuple"},{"internalType":"bool","name":"killed","type":"bool"},{"internalType":"uint256","name":"totalVotes","type":"uint256"},{"internalType":"uint256","name":"userVotes","type":"uint256"},{"internalType":"uint256","name":"userClaimable","type":"uint256"},{"internalType":"uint256","name":"emissionRate","type":"uint256"},{"internalType":"uint256","name":"userEmissionRate","type":"uint256"},{"internalType":"uint256","name":"stakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"userStakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"averageInterestRatePerSecond","type":"uint256"},{"internalType":"uint256","name":"userInterestRatePerSecond","type":"uint256"},{"internalType":"Token[]","name":"stakeableTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedAmounts","type":"uint256[]"},{"internalType":"uint256[]","name":"userStakedAmounts","type":"uint256[]"},{"internalType":"Token[]","name":"underlyingTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedUnderlying","type":"uint256[]"},{"internalType":"uint256[]","name":"userUnderlying","type":"uint256[]"},{"components":[{"internalType":"Token[]","name":"tokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"rates","type":"uint256[]"},{"internalType":"uint256[]","name":"userClaimable","type":"uint256[]"},{"internalType":"uint256[]","name":"userRates","type":"uint256[]"}],"internalType":"struct BribeData[]","name":"bribes","type":"tuple[]"}],"internalType":"struct GaugeData[]","name":"gaugeDataArray","type":"tuple[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IPool","name":"poolAddr","type":"address"},{"internalType":"Token","name":"token","type":"bytes32"}],"name":"getPoolBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"gauge","type":"address"},{"internalType":"address","name":"user","type":"address"}],"name":"queryGauge","outputs":[{"components":[{"internalType":"address","name":"gauge","type":"address"},{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"poolData","type":"tuple"},{"internalType":"bool","name":"killed","type":"bool"},{"internalType":"uint256","name":"totalVotes","type":"uint256"},{"internalType":"uint256","name":"userVotes","type":"uint256"},{"internalType":"uint256","name":"userClaimable","type":"uint256"},{"internalType":"uint256","name":"emissionRate","type":"uint256"},{"internalType":"uint256","name":"userEmissionRate","type":"uint256"},{"internalType":"uint256","name":"stakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"userStakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"averageInterestRatePerSecond","type":"uint256"},{"internalType":"uint256","name":"userInterestRatePerSecond","type":"uint256"},{"internalType":"Token[]","name":"stakeableTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedAmounts","type":"uint256[]"},{"internalType":"uint256[]","name":"userStakedAmounts","type":"uint256[]"},{"internalType":"Token[]","name":"underlyingTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedUnderlying","type":"uint256[]"},{"internalType":"uint256[]","name":"userUnderlying","type":"uint256[]"},{"components":[{"internalType":"Token[]","name":"tokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"rates","type":"uint256[]"},{"internalType":"uint256[]","name":"userClaimable","type":"uint256[]"},{"internalType":"uint256[]","name":"userRates","type":"uint256[]"}],"internalType":"struct BribeData[]","name":"bribes","type":"tuple[]"}],"internalType":"struct GaugeData","name":"poolData","type":"tuple"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"}],"name":"queryPool","outputs":[{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"ret","type":"tuple"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract ISwap","name":"swap","type":"address"},{"internalType":"Token","name":"base","type":"bytes32"},{"internalType":"Token","name":"quote","type":"bytes32"},{"internalType":"uint256","name":"baseAmount","type":"uint256"}],"name":"spotPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token","name":"quote","type":"bytes32"},{"internalType":"Token[]","name":"tok","type":"bytes32[]"},{"internalType":"uint256[]","name":"amount","type":"uint256[]"}],"name":"spotPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token","name":"base","type":"bytes32"},{"internalType":"Token","name":"quote","type":"bytes32"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"spotPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"Token[]","name":"ts","type":"bytes32[]"}],"name":"userBalances","outputs":[{"internalType":"uint256[]","name":"balances","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"wombatGauges","outputs":[{"components":[{"internalType":"address","name":"gauge","type":"address"},{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"poolData","type":"tuple"},{"internalType":"bool","name":"killed","type":"bool"},{"internalType":"uint256","name":"totalVotes","type":"uint256"},{"internalType":"uint256","name":"userVotes","type":"uint256"},{"internalType":"uint256","name":"userClaimable","type":"uint256"},{"internalType":"uint256","name":"emissionRate","type":"uint256"},{"internalType":"uint256","name":"userEmissionRate","type":"uint256"},{"internalType":"uint256","name":"stakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"userStakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"averageInterestRatePerSecond","type":"uint256"},{"internalType":"uint256","name":"userInterestRatePerSecond","type":"uint256"},{"internalType":"Token[]","name":"stakeableTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedAmounts","type":"uint256[]"},{"internalType":"uint256[]","name":"userStakedAmounts","type":"uint256[]"},{"internalType":"Token[]","name":"underlyingTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedUnderlying","type":"uint256[]"},{"internalType":"uint256[]","name":"userUnderlying","type":"uint256[]"},{"components":[{"internalType":"Token[]","name":"tokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"rates","type":"uint256[]"},{"internalType":"uint256[]","name":"userClaimable","type":"uint256[]"},{"internalType":"uint256[]","name":"userRates","type":"uint256[]"}],"internalType":"struct BribeData[]","name":"bribes","type":"tuple[]"}],"internalType":"struct GaugeData[]","name":"gaugeDataArray","type":"tuple[]"}],"stateMutability":"nonpayable","type":"function"}]

VELOCORE_V2_VAULT_ABI = [{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeAttached","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IConverter","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Convert","type":"event"},{"anonymous":False,"inputs":[{"components":[{"internalType":"address","name":"facetAddress","type":"address"},{"internalType":"enum IVault.FacetCutAction","name":"action","type":"uint8"},{"internalType":"bytes4[]","name":"functionSelectors","type":"bytes4[]"}],"indexed":False,"internalType":"struct IVault.FacetCut[]","name":"_diamondCut","type":"tuple[]"},{"indexed":False,"internalType":"address","name":"_init","type":"address"},{"indexed":False,"internalType":"bytes","name":"_calldata","type":"bytes"}],"name":"DiamondCut","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Gauge","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":False,"internalType":"bool","name":"killed","type":"bool"}],"name":"GaugeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract ISwap","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Swap","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"UserBalance","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"int256","name":"voteDelta","type":"int256"}],"name":"Vote","type":"event"},{"inputs":[{"internalType":"contract IFacet","name":"implementation","type":"address"}],"name":"admin_addFacet","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"t","type":"bool"}],"name":"admin_pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IAuthorizer","name":"auth_","type":"address"}],"name":"admin_setAuthorizer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"implementation","type":"address"},{"internalType":"bytes4[]","name":"sigs","type":"bytes4[]"}],"name":"admin_setFunctions","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"treasury","type":"address"}],"name":"admin_setTreasury","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"i","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"attachBribe","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"ballotToken","outputs":[{"internalType":"Token","name":"","type":"bytes32"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"emissionToken","outputs":[{"internalType":"Token","name":"","type":"bytes32"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"internalType":"int128[]","name":"deposit","type":"int128[]"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"bytes32[]","name":"tokenInformations","type":"bytes32[]"},{"internalType":"bytes","name":"data","type":"bytes"}],"internalType":"struct VelocoreOperation[]","name":"ops","type":"tuple[]"}],"name":"execute","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"uint8","name":"method","type":"uint8"},{"internalType":"address","name":"t1","type":"address"},{"internalType":"uint8","name":"m1","type":"uint8"},{"internalType":"int128","name":"a1","type":"int128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"execute1","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"uint8","name":"method","type":"uint8"},{"internalType":"address","name":"t1","type":"address"},{"internalType":"uint8","name":"m1","type":"uint8"},{"internalType":"int128","name":"a1","type":"int128"},{"internalType":"address","name":"t2","type":"address"},{"internalType":"uint8","name":"m2","type":"uint8"},{"internalType":"int128","name":"a2","type":"int128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"execute2","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"uint8","name":"method","type":"uint8"},{"internalType":"address","name":"t1","type":"address"},{"internalType":"uint8","name":"m1","type":"uint8"},{"internalType":"int128","name":"a1","type":"int128"},{"internalType":"address","name":"t2","type":"address"},{"internalType":"uint8","name":"m2","type":"uint8"},{"internalType":"int128","name":"a2","type":"int128"},{"internalType":"address","name":"t3","type":"address"},{"internalType":"uint8","name":"m3","type":"uint8"},{"internalType":"int128","name":"a3","type":"int128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"execute3","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"_functionSelector","type":"bytes4"}],"name":"facetAddress","outputs":[{"internalType":"address","name":"facetAddress_","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"facetAddresses","outputs":[{"internalType":"address[]","name":"facetAddresses_","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_facet","type":"address"}],"name":"facetFunctionSelectors","outputs":[{"internalType":"bytes4[]","name":"facetFunctionSelectors_","type":"bytes4[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"facets","outputs":[{"components":[{"internalType":"address","name":"facetAddress","type":"address"},{"internalType":"bytes4[]","name":"functionSelectors","type":"bytes4[]"}],"internalType":"struct IVault.Facet[]","name":"facets_","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"t0","type":"address"},{"internalType":"address","name":"t1","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"killBribe","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"bool","name":"t","type":"bool"}],"name":"killGauge","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token","name":"","type":"bytes32"},{"internalType":"uint128","name":"","type":"uint128"},{"internalType":"uint128","name":"","type":"uint128"}],"name":"notifyInitialSupply","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"internalType":"int128[]","name":"deposit","type":"int128[]"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"bytes32[]","name":"tokenInformations","type":"bytes32[]"},{"internalType":"bytes","name":"data","type":"bytes"}],"internalType":"struct VelocoreOperation[]","name":"ops","type":"tuple[]"}],"name":"query","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"uint8","name":"method","type":"uint8"},{"internalType":"address","name":"t1","type":"address"},{"internalType":"uint8","name":"m1","type":"uint8"},{"internalType":"int128","name":"a1","type":"int128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"query1","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"uint8","name":"method","type":"uint8"},{"internalType":"address","name":"t1","type":"address"},{"internalType":"uint8","name":"m1","type":"uint8"},{"internalType":"int128","name":"a1","type":"int128"},{"internalType":"address","name":"t2","type":"address"},{"internalType":"uint8","name":"m2","type":"uint8"},{"internalType":"int128","name":"a2","type":"int128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"query2","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"uint8","name":"method","type":"uint8"},{"internalType":"address","name":"t1","type":"address"},{"internalType":"uint8","name":"m1","type":"uint8"},{"internalType":"int128","name":"a1","type":"int128"},{"internalType":"address","name":"t2","type":"address"},{"internalType":"uint8","name":"m2","type":"uint8"},{"internalType":"int128","name":"a2","type":"int128"},{"internalType":"address","name":"t3","type":"address"},{"internalType":"uint8","name":"m3","type":"uint8"},{"internalType":"int128","name":"a3","type":"int128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"query3","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]

GAS_ORACLE_ABI = [
    {
        "type": "function",
        "name": "getL1Fee",
        "stateMutability": "view",
        "inputs": [{"internalType": "bytes", "name": "_data", "type": "bytes"}],
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}]
    }
]
