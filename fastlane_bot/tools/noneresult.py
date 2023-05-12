"""
a none object that behaves somewhat more gracefully than None

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__ = "12/May/2023"

def isNone(none):
    """returns True if none is None or NoneResult()"""
    return isinstance(none, NoneResult) or none is None

class NoneResult():
    """
    a NoneResult is a dummy object that behave more gracefully than None
    
    
    typically a NoneResult is an error result that can be passed down without
    raising errors in situations where None would fail
    
    :message:   typically provides the (error) message that caused the creation of this object
                it can be accessed via the `__message` attribute
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    def __init__(self, message=None):
        self.__message = str(message)
        #print('[NoneResult] message:', message, self._message)
        
    def __getattr__(self, attr):
        return self
    
    def __getitem__(self, key):
        return self
    
    # conversions and other unitary operations
    def __str__(self):
        return f"NoneResult('{self.__message}')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __bool__(self):
        return False
    
    def __hash__(self):
        return hash(None)
    
    def __int__(self):
        return 0
    
    def __oct__(self):
        return oct(0)
    
    def __hex__(self):
        return hex(0)
    
    def __trunc__(self):
        return self
    
    def __float__(self):
        return 0.0
    
    def __format__(self, fmt):
        return str(self).__format__(fmt)
    
    def __floor__(self):
        return self
    
    def __ceil__(self):
        return self
    
    def __abs__(self):
        return self
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return self
    
    def __round__(self, n):
        return self
    
    # binary operations (all return self)
    def __add__(self, other):
        return self
    
    def __sub__(self, other):
        return self
    
    def __mul__(self, other):
        return self
    
    def __truediv__(self, other):
        return self
    
    def __floordiv__(self, other):
        return self
    
    def __divmod__(self, other):
        return self
    
    def __pow__(self, other):
        return self
    
    def __mod__(self, other):
        return self
    
    def __sizeof__(self):
        return 0
    
    # reflected binary operations ditto
    def __radd__(self, other):
        return self
    
    def __rsub__(self, other):
        return self
    
    def __rmul__(self, other):
        return self
    
    def __rtruediv__(self, other):
        return self
    
    def __rfloordiv__(self, other):
        return self
    
    def __rdivmod__(self, other):
        return self
    
    def __rpow__(self, other):
        return self
    
    def __rmod__(self, other):
        return self
    
    # comparison operators (all False, except with other NoneResult)
    def __eq__(self, other):
        if isinstance(other, NoneResult) or other is None:
            return True
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return False
    
    def __le__(self, other):
        return False
    
    def __gt__(self, other):
        return False
    
    def __ge__(self, other):
        return False
    
    