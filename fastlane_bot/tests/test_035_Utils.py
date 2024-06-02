# ------------------------------------------------------------
# Auto generated test file `test_035_Utils.py`
# ------------------------------------------------------------
# source file   = NBTest_035_Utils.py
# test id       = 035
# test comment  = Utils
# ------------------------------------------------------------



from web3.datastructures import AttributeDict
from web3.types import HexBytes

from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot
from fastlane_bot.events.interfaces.event import Event
from fastlane_bot.events.pools import UniswapV2Pool, UniswapV3Pool, BancorV3Pool, CarbonV1Pool
from fastlane_bot.events.utils import filter_latest_events, complex_handler

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3Pool))
from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)



class MockManager():

    pool_data = pd.DataFrame({'anchor': ['0xabc', '0xdef'], 'exchange_name': ['bancor_v2', 'bancor_v2']}).to_dict('records')

    def pool_type_from_exchange_name(self, exchange_name):

        class MockPoolType():

            def unique_key(self):
                return 'address'
        return MockPoolType()

    def exchange_name_from_event(self, event):
        return 'uniswap_v2'
mocked_mgr = MockManager()

event1 = Event.from_dict({'args': {'reserve0': 100, 'reserve1': 100}, 'event': 'Sync', 'address': '0xabc', 'blockNumber': 5, 'transactionIndex': 0, 'logIndex': 0, 'transactionHash': '', 'blockHash': ''})
event2 = Event.from_dict({'args': {'reserve0': 200, 'reserve1': 200}, 'event': 'Sync', 'address': '0xabc', 'blockNumber': 10, 'transactionIndex': 1, 'logIndex': 1, 'transactionHash': '', 'blockHash': ''})
event3 = Event.from_dict({'args': {'reserve0': 300, 'reserve1': 300}, 'event': 'Sync', 'address': '0xdef', 'blockNumber': 7, 'transactionIndex': 1, 'logIndex': 1, 'transactionHash': '', 'blockHash': ''})
mock_events = [event1, event2, event3]


# ------------------------------------------------------------
# Test      035
# File      test_035_Utils.py
# Segment   test_filter_latest_events
# ------------------------------------------------------------
def test_test_filter_latest_events():
# ------------------------------------------------------------
    
    result = filter_latest_events(mocked_mgr, mock_events)
    assert (len(result) == len({event.address for event in result}))
    pool_address = result[0].address
    pool_events = [event for event in mock_events if (event.address == pool_address)]
    

# ------------------------------------------------------------
# Test      035
# File      test_035_Utils.py
# Segment   test_complex_handler
# ------------------------------------------------------------
def test_test_complex_handler():
# ------------------------------------------------------------
    
    attribute_dict = AttributeDict({'a': 1, 'b': 2})
    assert (complex_handler(attribute_dict) == {'a': 1, 'b': 2})
    hex_bytes = HexBytes(b'hello')
    assert (complex_handler(hex_bytes) == '0x68656c6c6f')
    dictionary = {'a': 1, 'b': HexBytes(b'hello'), 'c': AttributeDict({'d': 4})}
    assert (complex_handler(dictionary) == {'a': 1, 'b': '0x68656c6c6f', 'c': {'d': 4}})
    list_ = [1, HexBytes(b'hello'), AttributeDict({'d': 4})]
    assert (complex_handler(list_) == [1, '0x68656c6c6f', {'d': 4}])
    set_ = {1, 2, 3}
    assert (complex_handler(set_) == [1, 2, 3])
    assert (complex_handler(123) == 123)