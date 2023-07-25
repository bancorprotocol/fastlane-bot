"""
optimization library -- dataclass base module

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

This module is still subject to active research, and comments and suggestions are welcome. 
The corresponding author is Stefan Loesch <stefan@bancor.network>
"""
from dataclasses import dataclass, field, fields, asdict, astuple, InitVar


class DCBase:
    """
    base class for all data classes, adding some useful methods
    """

    def asdict(self):
        return asdict(self)

    def astuple(self):
        return astuple(self)

    def fields(self):
        return fields(self)

    # def pickle(self, filename, addts=True):
    #     """
    #     pickles the object to a file
    #     """
    #     if addts:
    #         filename = f"{filename}.{time.time()}.pickle"
    #     with open(filename, 'wb') as f:
    #         pickle.dump(self, f)

    # @classmethod
    # def unpickle(cls, filename):
    #     """
    #     unpickles the object from a file
    #     """
    #     with open(filename, 'rb') as f:
    #         object = pickle.load(f)
    #     assert isinstance(object, cls), f"unpickled object is not of type {cls}"
    #     return object

