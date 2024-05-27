import pytest

from fastlane_bot.events.exchanges.carbon_v1 import CarbonV1
from fastlane_bot.events.exchanges.bancor_pol import BancorPol
from fastlane_bot.events.exchanges.bancor_v2 import BancorV2
from fastlane_bot.events.exchanges.bancor_v3 import BancorV3
from fastlane_bot.events.exchanges.uniswap_v2 import UniswapV2
from fastlane_bot.events.exchanges.uniswap_v3 import UniswapV3
from fastlane_bot.events.exchanges.balancer import Balancer
from fastlane_bot.events.exchanges.solidly_v2 import SolidlyV2


@pytest.mark.parametrize("cls,exchange_name,event_topics", [
    (CarbonV1, "carbon_v1", {
        "StrategyCreated": "0xff24554f8ccfe540435cfc8854831f8dcf1cf2068708cfaf46e8b52a4ccc4c8d",
        "StrategyUpdated": "0x720da23a5c920b1d8827ec83c4d3c4d90d9419eadb0036b88cb4c2ffa91aef7d",
        "StrategyDeleted": "0x4d5b6e0627ea711d8e9312b6ba56f50e0b51d41816fd6fd38643495ac81d38b6",
        "PairTradingFeePPMUpdated": "0x831434d05f3ad5f63be733ea463b2933c70d2162697fd200a22b5d56f5c454b6",
        "TradingFeePPMUpdated": "0x66db0986e1156e2e747795714bf0301c7e1c695c149a738cb01bcf5cfead8465",
        "PairCreated": "0x6365c594f5448f79c1cc1e6f661bdbf1d16f2e8f85747e13f8e80f1fd168b7c3",
    }),
    (BancorPol, "bancor_pol", {
        "TokenTraded": "0x16ddee9b3f1b2e6f797172fe2cd10a214e749294074e075e451f95aecd0b958c",
        "TradingEnabled": "0xae3f48c001771f8e9868e24d47b9e4295b06b1d78072acf96f167074aa3fab64",
    }),
    (BancorV2, "bancor_v2", {
        "TokenRateUpdate": "0x77f29993cf2c084e726f7e802da0719d6a0ade3e204badc7a3ffd57ecb768c24",
    }),
    (BancorV3, "bancor_v3", {
        "TradingLiquidityUpdated": "0x6e96dc5343d067ec486a9920e0304c3610ed05c65e45cc029d9b9fe7ecfa7620",
        # "TotalLiquidityUpdated": "0x85a03952f50b8c00b32a521c32094023b64ef0b6d4511f423d44c480a62cb145",
    }),
    (UniswapV2, "uniswap_v2", {
        "Sync": "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1",
    }),
    (UniswapV3, "uniswap_v3", {
        "Swap": "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
    }),
    (UniswapV3, "pancakeswap_v3", {
        "Swap": "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83",
    }),
    (Balancer, "balancer", {}),
    (SolidlyV2, "velocimeter_v2", {
        "Sync": "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a",
    }),
])
def test_event_topic(config, cls, exchange_name, event_topics):
    exchange = cls(exchange_name=exchange_name)
    for subscription in exchange.get_subscriptions(config.w3):
        assert event_topics.pop(subscription._event.event_name) == subscription.topic
    assert event_topics == {}
