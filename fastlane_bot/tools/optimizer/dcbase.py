"""
This module defines the `DCBase` class, from which
dataclasses can derive, and which adds useful methods to
those dataclasses, notably ``asdict``, ``astuple`` and ``fields``.

---
(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
from dataclasses import dataclass, field, fields, asdict, astuple, InitVar


class DCBase:
    """
    Adds useful methods to dataclasses
    
    USAGE
    
    .. code-block:: python
    
        @dataclass
        class MyDataClass(DCBase):
            ...
        
        obj = MyDataClass(...)
        obj.asdict()
        obj.astuple()
        obj.fields()
    """

    def asdict(self):
        """
        returns the object as a dict
        
        alias for `dataclasses.asdict(self)`
        """
        return asdict(self)

    def astuple(self):
        """
        returns the object as a tuple
        
        alias for `dataclasses.astuple(self)`
        """
        return astuple(self)

    def fields(self):
        """
        returns the object fields
        
        alias for `dataclasses.fields(self)`
        """
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

