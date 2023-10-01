from .Pool1 import Pool1
from .Pool2 import Pool2
from .Pool3 import Pool3
from .Pool4 import Pool4
from .Pool5 import Pool5
from .Pool6 import Pool6
from .Pool7 import Pool7
from .Pool8 import Pool8
from .Pool9 import Pool9
from .Coin1 import Coin1
from .Coin2 import Coin2
from .Coin3 import Coin3
from .Coin4 import Coin4
from .Coin5 import Coin5

params = {
    'link'    : {'type': Pool1, 'address': '0xF178C0b5Bb7e7aBF4e12A4838C7b7c5bA2C623c0', 'coins': [Coin1, Coin1]},
    'seth'    : {'type': Pool1, 'address': '0xc5424B857f758E906013F3555Dad202e4bdB4567', 'coins': [Coin1, Coin1]},
    'steth'   : {'type': Pool2, 'address': '0xDC24316b9AE028F1497c275EB9192a3Ea0f67022', 'coins': [Coin1, Coin1]},
    'aave'    : {'type': Pool3, 'address': '0xDeBF20617708857ebe4F679508E7b7863a8A8EeE', 'coins': [Coin1, Coin1, Coin1]},
    'saave'   : {'type': Pool3, 'address': '0xEB16Ae0052ed37f479f7fe63849198Df1765a733', 'coins': [Coin1, Coin1]},
    'eurs'    : {'type': Pool4, 'address': '0x0Ce6a5fF5217e38315f87032CF90686C96627CAA', 'coins': [Coin5, Coin5]},
    '3pool'   : {'type': Pool5, 'address': '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7', 'coins': [Coin5, Coin5, Coin5]},
    'hbtc'    : {'type': Pool5, 'address': '0x4CA9b3063Ec5866A4B82E437059D2C43d1be596F', 'coins': [Coin5, Coin5]},
    'ren'     : {'type': Pool6, 'address': '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', 'coins': [Coin2, Coin5]},
    'sbtc'    : {'type': Pool6, 'address': '0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714', 'coins': [Coin2, Coin5, Coin5]},
    'pax'     : {'type': Pool7, 'address': '0x06364f10B501e868329afBc005b3492902d6C763', 'coins': [Coin3, Coin3, Coin3, Coin5]},
    'ib'      : {'type': Pool8, 'address': '0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF', 'coins': [Coin4, Coin4, Coin4]},
    'yv2'     : {'type': Pool8, 'address': '0x8925D9d9B4569D737a48499DeF3f67BaA5a144b9', 'coins': [Coin4, Coin4, Coin4]},
    'bbtc'    : {'type': Pool9, 'address': '0x071c661B4DeefB59E2a3DdB20Db036821eeE8F4b', 'coins': [Coin1, Coin1]},
    'dusd'    : {'type': Pool9, 'address': '0x8038C01A0390a8c547446a0b2c18fc9aEFEcc10c', 'coins': [Coin1, Coin1]},
    'gusd'    : {'type': Pool9, 'address': '0x4f062658EaAF2C1ccf8C8e36D6824CDf41167956', 'coins': [Coin1, Coin1]},
    'husd'    : {'type': Pool9, 'address': '0x3eF6A01A0f81D6046290f3e2A8c5b843e738E604', 'coins': [Coin1, Coin1]},
    'linkusd' : {'type': Pool9, 'address': '0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171', 'coins': [Coin1, Coin1]},
    'musd'    : {'type': Pool9, 'address': '0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6', 'coins': [Coin1, Coin1]},
    'obtc'    : {'type': Pool9, 'address': '0xd81dA8D904b52208541Bade1bD6595D8a251F8dd', 'coins': [Coin1, Coin1]},
    'pbtc'    : {'type': Pool9, 'address': '0x7F55DDe206dbAD629C080068923b36fe9D6bDBeF', 'coins': [Coin1, Coin1]},
    'rsv'     : {'type': Pool9, 'address': '0xC18cC39da8b11dA8c3541C598eE022258F9744da', 'coins': [Coin1, Coin1]},
    'tbtc'    : {'type': Pool9, 'address': '0xC25099792E9349C7DD09759744ea681C7de2cb66', 'coins': [Coin1, Coin1]},
    'usdk'    : {'type': Pool9, 'address': '0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb', 'coins': [Coin1, Coin1]},
    'usdn'    : {'type': Pool9, 'address': '0x0f9cb53Ebe405d49A0bbdBD291A65Ff571bC83e1', 'coins': [Coin1, Coin1]},
    'usdp'    : {'type': Pool9, 'address': '0x42d7025938bEc20B69cBae5A77421082407f053A', 'coins': [Coin1, Coin1]},
    'ust'     : {'type': Pool9, 'address': '0x890f4e345B1dAED0367A877a1612f86A1f86985f', 'coins': [Coin1, Coin1]},
}

def make_pool(pool_name: str, read_init=False, read_sync=False, mock_data={}) -> any:
    class Pool(params[pool_name]['type']):
        def read(self, init: bool, sync: bool):
            self._read(params[pool_name]['address'], params[pool_name]['coins'], init, sync)
        def mock(self, data: dict):
            def get(val: any) -> any:
                if type(val) is dict:
                    return Object(val)
                if type(val) is list:
                    return [get(v) for v in val]
                return val
            class Object:
                def __init__(self, data: dict):
                    for key, val in data.items():
                        setattr(self, key, get(val))
            for key, val in data.items():
                setattr(self, key, get(val))
    pool = Pool()
    pool.read(read_init, read_sync)
    pool.mock(mock_data)
    return pool
