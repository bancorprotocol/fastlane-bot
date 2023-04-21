"""
Carbon helper module - parameter management
"""
__VERSION__ = "1.2"
__DATE__ = "29/01/2023"


class Params:
    """
    parameter management

    EXAMPLE

        # Standard

        p = Params(a=1, b=2)
        p.a            # 1
        p["b"]         # 2
        p.c            # raises; must exists when accessed as attribute
        p["c"]         # None; fails gracefully when accessed via []
        p["c"] = 3     # OK
        p.c            # 3; after assignment
        p["c"]         # 3; after assignment
        p["b"] = 3     # raises; re-assignment not allowed

        p = Params(**{"a": 1, "b": 2})  # creating params from dict

        # With defaults

        p = Params(a=1, b=2)
        p.set_default(**{"b":20, "c":3})
        p.a                           # 1; from params
        p.b                           # 2; from params
        p.c                           # 3; from defaults


    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def __init__(self, **kwargs):
        self._params = dict(kwargs)
        self._defaults = None

    @classmethod
    def construct(cls, dct=None, defaults=None):
        """
        alternative constructor from dct

        :dct:       typically a dict object; can also be a Params object which will be replicated
                    (defaults can either be on the original object or here, but not on both; if
                    you want to merge defaults use set_default on the created object); a value
                    of None creates an empty object
        :defaults:  the default values for this object; note that they can not be passed
                    using the standard constructor; if the object is already a params object,
                    the existing defaults will be updated, and overwritten if they exist
        :returns:   a newly created Params object
        """
        if not dct:
            result = cls()
        elif isinstance(dct, cls):
            result = cls(**dct._params)
            if not dct._defaults is None and not defaults is None:
                raise ValueError(
                    "Must not provide default in both constructor and dct",
                    dct,
                    defaults,
                )
        else:
            result = cls(**dct)

        if defaults:
            result._defaults = {**defaults}
        return result

    def add(self, **kwargs):
        """
        adds additional parameters from kwargs (params must not yet exist)

        :returns:     self (for chaining)
        """
        for k, v in kwargs.items():
            self[k] = v
        return self

    def get_default(self, item, raiseonerror=False):
        """
        gets the default value (None if does not exist)
        """
        if self._defaults is None:
            self.set_default()
        if raiseonerror:
            return self._defaults[item]
        else:
            return self._defaults.get(item, None)

    def set_default(self, **kwargs):
        """
        adds default params

        :returns:    self for chaining
        """
        if self._defaults is None:
            self._defaults = dict()
        else:
            for k, v in kwargs.items():
                self._defaults[k] = v
        return self

    @property
    def params(self):
        """
        returns the parameters as dict
        """
        return self._params

    @property
    def defaults(self):
        """
        returns defaults object (creates empty one if it does not exist)
        """
        if self._defaults is None:
            self.set_default()
        return self._defaults

    def set(self, item, value, allowupdate=True):
        """
        sets an item

        :item:          the item to be set
        :value:         the value to set it to
        :allowupdate:   if True (default), existing items can be changed
        :returns:       self (for chaining)
        """
        if not allowupdate:
            if item in self._params:
                raise ValueError(
                    f"Item {item} already exists with value {self._params[item]} and update not allowed.",
                    value,
                    self._params,
                    allowupdate,
                )
        self._params[item] = value
        return self

    def __getitem__(self, item):
        try:
            return self._params[item]
        except KeyError:
            return self.get_default(item, raiseonerror=False)

    def __setitem__(self, item, value):
        self.set(item, value, allowupdate=False)

    def __getattr__(self, item):
        """
        for all item starting with _ this refers to super().__getattr__
        """
        if item[:1] == "_":
            return super().__getattr__(item)
        try:
            return self._params[item]
        except KeyError:
            return self.get_default(item, raiseonerror=True)

    def __repr__(self):

        defaults = f", defaults={self._defaults}" if self._defaults else ""
        return f"{self.__class__.__name__}.construct({self._params}{defaults})"
