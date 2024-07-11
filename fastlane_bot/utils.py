"""
Various utility functions

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from glob import glob
from os.path import join
from decimal import Decimal


def safe_int(value) -> int:
    int_value = int(value)
    assert value == int_value, f"non-integer `float` value {value}"
    return int_value


def find_latest_timestamped_folder(logging_path=None):
    """
    Find the latest timestamped folder in the given directory or the default directory.

    Args:
        logging_path (str, optional): The custom logging path where the timestamped folders are. Defaults to None.

    Returns:
        str: Path to the latest timestamped folder, or None if no folder is found.
    """
    search_path = logging_path if logging_path else "."
    search_path = join(search_path, "logs/*")
    list_of_folders = glob(search_path)

    if not list_of_folders:
        return None

    list_of_folders.sort(reverse=True)  # Sort the folders in descending order
    return list_of_folders[0]  # The first one is the latest


ONE = 2 ** 48

MAX_UINT128 = 2 ** 128 - 1
MAX_UINT256 = 2 ** 256 - 1

def check(val, max): assert 0 <= val <= max; return val

def uint128(n): return check(n, MAX_UINT128)
def add(a, b): return check(a + b, MAX_UINT256)
def sub(a, b): return check(a - b, MAX_UINT256)
def mul(a, b): return check(a * b, MAX_UINT256)
def mulDivF(a, b, c): return check(a * b // c, MAX_UINT256)
def mulDivC(a, b, c): return check((a * b + c - 1) // c, MAX_UINT256)

def bitLength(value: int) -> int:
    return len(bin(value).lstrip('0b')) if value > 0 else 0

def encodeRate(value: Decimal) -> int:
    data = int(value.sqrt() * ONE)
    length = bitLength(data // ONE)
    return (data >> length) << length

def decodeRate(value: Decimal) -> Decimal:
  return (value / ONE) ** 2

def encodeFloat(value: int) -> int:
    exponent = bitLength(value // ONE)
    mantissa = value >> exponent
    return mantissa | (exponent * ONE)

def decodeFloat(value: int) -> int:
    return (value % ONE) << (value // ONE)

def encodeOrder(order: dict) -> dict:
    y = int(order['liquidity'])
    L = encodeRate(Decimal(order['lowestRate']))
    H = encodeRate(Decimal(order['highestRate']))
    M = encodeRate(Decimal(order['marginalRate']))
    return {
        'y' : y,
        'z' : y if H == M else y * (H - L) // (M - L),
        'A' : encodeFloat(H - L),
        'B' : encodeFloat(L),
    }

def decodeOrder(order: dict) -> dict:
    y = Decimal(order['y'])
    z = Decimal(order['z'])
    A = Decimal(decodeFloat(order['A']))
    B = Decimal(decodeFloat(order['B']))
    return {
        'liquidity'    : y,
        'lowestRate'   : decodeRate(B),
        'highestRate'  : decodeRate(B + A),
        'marginalRate' : decodeRate(B + A if y == z else B + A * y / z),
    }

#
#      x * (A * y + B * z) ^ 2
# ---------------------------------
#  A * x * (A * y + B * z) + z ^ 2
#
def tradeBySourceAmountFunc(x, y, z, A, B):
    if (A == 0):
        return mulDivF(x, mul(B, B), mul(ONE, ONE))

    temp1 = mul(z, ONE)
    temp2 = add(mul(y, A), mul(z, B))
    temp3 = mul(temp2, x)

    factor1 = mulDivC(temp1, temp1, MAX_UINT256)
    factor2 = mulDivC(temp3, A, MAX_UINT256)
    factor = max(factor1, factor2)

    temp4 = mulDivC(temp1, temp1, factor)
    temp5 = mulDivC(temp3, A, factor)
    if temp4 + temp5 <= MAX_UINT256:
        return mulDivF(temp2, temp3 // factor, temp4 + temp5)
    return temp2 // add(A, mulDivC(temp1, temp1, temp3))

#
#                  x * z ^ 2
# -------------------------------------------
#  (A * y + B * z) * (A * y + B * z - A * x)
#
def tradeByTargetAmountFunc(x, y, z, A, B):
    if (A == 0):
        return mulDivC(x, mul(ONE, ONE), mul(B, B))

    temp1 = mul(z, ONE)
    temp2 = add(mul(y, A), mul(z, B))
    temp3 = sub(temp2, mul(x, A))

    factor1 = mulDivC(temp1, temp1, MAX_UINT256)
    factor2 = mulDivC(temp2, temp3, MAX_UINT256)
    factor = max(factor1, factor2)

    temp4 = mulDivC(temp1, temp1, factor)
    temp5 = mulDivF(temp2, temp3, factor)
    return mulDivC(x, temp4, temp5)

def tradeFunc(amount, order, func, fallback):
    x = amount
    y = order['y']
    z = order['z']
    A = decodeFloat(order['A'])
    B = decodeFloat(order['B'])
    try:
        return uint128(func(x, y, z, A, B))
    except:
        return fallback

def tradeBySourceAmount(amount: int, order: dict) -> int:
    return tradeFunc(amount, order, tradeBySourceAmountFunc, 0)

def tradeByTargetAmount(amount: int, order: dict) -> int:
    return tradeFunc(amount, order, tradeByTargetAmountFunc, MAX_UINT128)
