from fastlane_bot.events.exchanges.carbon_v1 import CarbonV1
from fastlane_bot.events.exchanges.bancor_pol import BancorPol
from fastlane_bot.events.exchanges.bancor_v2 import BancorV2
from fastlane_bot.events.exchanges.bancor_v3 import BancorV3
from fastlane_bot.events.exchanges.uniswap_v2 import UniswapV2
from fastlane_bot.events.exchanges.uniswap_v3 import UniswapV3
from fastlane_bot.events.exchanges.solidly_v2 import SolidlyV2


def test_event_topics(manager):
    for exchange_name, exchange in manager.exchanges.items():
        contract = manager.event_contracts[exchange_name]
        for subscription in exchange.get_subscriptions(contract):
            if isinstance(exchange, CarbonV1):
                if subscription._event == contract.events.StrategyCreated:
                    assert subscription.topic == "0xff24554f8ccfe540435cfc8854831f8dcf1cf2068708cfaf46e8b52a4ccc4c8d"
                elif subscription._event == contract.events.StrategyUpdated:
                    assert subscription.topic == "0x720da23a5c920b1d8827ec83c4d3c4d90d9419eadb0036b88cb4c2ffa91aef7d"
                elif subscription._event == contract.events.StrategyDeleted:
                    assert subscription.topic == "0x4d5b6e0627ea711d8e9312b6ba56f50e0b51d41816fd6fd38643495ac81d38b6"
                elif subscription._event == contract.events.PairTradingFeePPMUpdated:
                    assert subscription.topic == "0x831434d05f3ad5f63be733ea463b2933c70d2162697fd200a22b5d56f5c454b6"
                elif subscription._event == contract.events.TradingFeePPMUpdated:
                    assert subscription.topic == "0x66db0986e1156e2e747795714bf0301c7e1c695c149a738cb01bcf5cfead8465"
                elif subscription._event == contract.events.PairCreated:
                    assert subscription.topic == "0x6365c594f5448f79c1cc1e6f661bdbf1d16f2e8f85747e13f8e80f1fd168b7c3"
            elif isinstance(exchange, BancorPol):
                if subscription._event == contract.events.TokenTraded:
                    assert subscription.topic == "0x16ddee9b3f1b2e6f797172fe2cd10a214e749294074e075e451f95aecd0b958c"
                if subscription._event == contract.events.TradingEnabled:
                    assert subscription.topic == "0xe695080c3c54317994bff9c7069120ba78f950937caeb98bf02d395abf2a2867"
            elif isinstance(exchange, BancorV2):
                if subscription._event == contract.events.TokenRateUpdate:
                    assert subscription.topic == "0x77f29993cf2c084e726f7e802da0719d6a0ade3e204badc7a3ffd57ecb768c24"
            elif isinstance(exchange, BancorV3):
                if subscription._event == contract.events.TradingLiquidityUpdated:
                    assert subscription.topic == "0x6e96dc5343d067ec486a9920e0304c3610ed05c65e45cc029d9b9fe7ecfa7620"
            elif isinstance(exchange, UniswapV2):
                if subscription._event == contract.events.Sync:
                    assert subscription.topic == "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
            elif isinstance(exchange, UniswapV3):
                if subscription._event == contract.events.Swap:
                    assert subscription.topic == "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
            elif isinstance(exchange, SolidlyV2):
                if subscription._event == contract.events.Sync:
                    assert subscription.topic == "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
            else:
                print(exchange_name)
                print(subscription)
                assert False
