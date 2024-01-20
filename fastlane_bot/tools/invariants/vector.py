"""
dict-based vectors 

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9'
__DATE__ = "18/Jan/2024"

from dataclasses import dataclass, asdict
import math

@dataclass
class DictVector():
    """
    represents a vector as a dict where different keys are orthogonal dimensions
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    vec: dict = None
    
    def __post_init__(self):
        if self.vec is None:
            self.vec = dict()
    
    @classmethod
    def null(cls):
        """
        create a null DictVector
        """
        return cls()
    
    @classmethod
    def new(cls, single_dict_argument=None, **kwargs):
        """
        create a new DictVector from kwargs
        """
        if not single_dict_argument is None:
            assert len(kwargs) == 0, "new must be called with either single_dict_argument or keyword arguments, not both"
            return cls(single_dict_argument)
        return cls(dict(**kwargs))
    n = new
    
    @property
    def norm(self):
        """
        the L2 norm of self, assuming all keys are orthogonal
        """
        return self.dict_norm(self.vec)
    
    def _kwargs(self, other=None):
        """
        additional kwargs for __init__ when creating a new object in derived classes
        
        IMPORTANT NOTE
        
        many of the below dunder methods call the constructor of the derived class,
        and this constructor may have additional arguments. For this to work, the 
        derived class must provide the additional arguments required by its 
        constructor in the _kwargs method.
        
        If other is provided then this is eg for an operator like __add__. In this
        case the _kwargs method can decide what to do. Eg in some cases self and 
        other may not be compatible, in which case _kwargs should throw an exception.
        """
        return dict()   
    
    def __getitem__(self, key):
        return self.vec.get(key, 0)
    
    # def __setitem__(self, key, value):
    #     self.vec[key] = value
    
    def __eq__(self, other):
        objs_eq = self.dict_eq(self.vec, other.vec)
        #print(f"[DictVector::eq] objs_eq = {objs_eq}")
        return objs_eq
        
    def __add__(self, other):
        return self.__class__(self.dict_add(self.vec, other.vec), **self._kwargs(other))
    
    def __sub__(self, other):
        return self.__class__(self.dict_sub(self.vec, other.vec), **self._kwargs(other))
    
    def __mul__(self, other):
        if isinstance(other, DictVector):
            return self.dict_sprod(self.vec, other.vec)
        return self.__class__(self.dict_smul(self.vec, other), **self._kwargs())
    
    def __truediv__(self, other):
        return self.__class__(self.dict_smul(self.vec, 1/other), **self._kwargs())
    
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __pos__(self):
        return self
    
    def __neg__(self):
        return self.__class__(self.dict_smul(self.vec, -1), **self._kwargs())
    
    def __abs__(self):
        return self.__class__({k: abs(v) for k, v in self.vec.items()}, **self._kwargs())
    
    def __round__(self, n=None):
        return self.__class__({k: round(v, n) for k, v in self.vec.items()}, **self._kwargs())
    
    def __floor__(self):
        return self.__class__({k: math.floor(v) for k, v in self.vec.items()}, **self._kwargs())
    
    def __ceil__(self):
        return self.__class__({k: math.ceil(v) for k, v in self.vec.items()}, **self._kwargs())
    
    def __trunc__(self):
        return self.__class__({k: math.trunc(v) for k, v in self.vec.items()}, **self._kwargs())
    
    def __iter__(self):
        return iter(self.vec)
    
    def __len__(self):
        return len([v for v in self.vec.values() if v!=0])
    
    def __bool__(self):
        return bool([v for v in self.vec.values() if v!=0])
    
    # def __hash__(self):
    #     return hash(tuple(sorted(self.vec.items())))
    
    def __copy__(self):
        return self.__class__(self.vec.copy())
    
    # def __deepcopy__(self, memo):
    #     return self.__class__({k: copy.deepcopy(v, memo) for k, v in self.vec.items()})
        
    def __contains__(self, key):
        return key in self.vec and self.vec[key] != 0
    
    def __missing__(self, key):
        return 0
    
    def __iadd__(self, other):
        self.vec = self.dict_add(self.vec, other.vec)
        return self 
    
    def __isub__(self, other):
        self.vec = self.dict_sub(self.vec, other.vec)
        return self
    
    def __imul__(self, other):
        self.vec = self.dict_smul(self.vec, other)
        return self
    
    def __itruediv__(self, other):
        self.vec = self.dict_smul(self.vec, 1/other)
        return self
    
    @classmethod
    def dict_add(cls, a, b):
        """
        add two dict-vectors a and b
        """
        return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}
    
    @classmethod
    def dict_sub(cls, a, b):
        """
        subtract two dict-vectors a and b
        """
        return {k: a.get(k, 0) - b.get(k, 0) for k in set(a) | set(b)}
    
    @classmethod
    def dict_smul(cls, a, s):
        """
        multiply dict-vector a by scalar s
        """
        return {k: v*s for k, v in a.items()}
    
    @classmethod
    def dict_sprod(cls, a, b):
        """
        multiply two dict-vectors a and b (scalar product)
        """
        return sum(a.get(k, 0) * b.get(k, 0) for k in set(a) | set(b))
    
    @classmethod
    def dict_norm(cls, a):
        """
        the L2 norm of dict-vector a
        """
        return sum(v**2 for v in a.values())**0.5
    
    @classmethod
    def dict_eq(cls, a, b, *, eps=0):
        """
        whether two dict-vectors a and b are equal (within eps, L1 norm)
        """
        diffvec = cls.dict_sub(a, b)
        if len(diffvec) == 0:
            return True
        return max(abs(v) for v in diffvec.values()) <= eps


V = DictVector.new

add = DictVector.dict_add
sub = DictVector.dict_sub
smul = DictVector.dict_smul
sprod = DictVector.dict_sprod
norm = DictVector.dict_norm
eq = DictVector.dict_eq
