"""
Various utility functions

NOTE: Those functions would more naturally fit in `helpers` 
TODO-MIKE, TODO-KEVIN: check how hard this is

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import glob
import random
import os.path
from decimal import Decimal


def safe_int(value: int or float) -> int:
    assert value == int(value), f"non-integer `float` value {value}"
    return int(value)


def num_format(value: int or float) -> str:
    try:
        return "{0:.4f}".format(value)
    except Exception:
        return str(value)


def rand_item(list_of_items: list, num_of_items: int) -> any:
    return random.choice(list_of_items[:min(max(num_of_items, 1), len(list_of_items))])


def find_latest_timestamped_folder(logging_path=None):
    """
    Find the latest timestamped folder in the given directory or the default directory.

    Args:
        logging_path (str, optional): The custom logging path where the timestamped folders are. Defaults to None.

    Returns:
        str: Path to the latest timestamped folder, or None if no folder is found.
    """
    search_path = logging_path if logging_path else "."
    search_path = os.path.join(search_path, "logs/*")
    list_of_folders = glob.glob(search_path)

    if not list_of_folders:
        return None

    list_of_folders.sort(reverse=True)  # Sort the folders in descending order
    return list_of_folders[0]  # The first one is the latest


ONE = 2**48


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
