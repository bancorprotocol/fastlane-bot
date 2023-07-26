"""
optimization library -- optimizer base module

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

This module is still subject to active research, and comments and suggestions are welcome. 
The corresponding author is Stefan Loesch <stefan@bancor.network>
"""
__VERSION__ = "5.0"
__DATE__ = "26/Jul/2023"

from dataclasses import dataclass, field, fields, asdict, astuple, InitVar
from abc import ABC, abstractmethod, abstractproperty
import pandas as pd
import numpy as np

import time
import math
import numbers
import pickle
from ..cpc import ConstantProductCurve as CPC, CPCInverter, CPCContainer
from sys import float_info
from .dcbase import DCBase

class OptimizerBase(ABC):
    """
    base class for all optimizers

    :problem:       the problem object (eg allowing to read `problem.status`)
    :result:        the return value of problem.solve
    :time:          the time it took to solve this problem (optional)
    :optimizer:     the optimizer object that created this result
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    @abstractproperty
    def kind(self):
        """
        returns the kind of optimizer (as str)
        """

    def pickle(self, basefilename, addts=True):
        """
        pickles the object to a file
        """
        if addts:
            filename = f"{basefilename}.{int(time.time()*100)}.optimizer.pickle"
        else:
            filename = f"{basefilename}.optimizer.pickle"
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def unpickle(cls, basefilename):
        """
        unpickles the object from a file
        """
        with open(f"{basefilename}.optimizer.pickle", "rb") as f:
            object = pickle.load(f)
        assert isinstance(object, cls), f"unpickled object is not of type {cls}"
        return object

    @dataclass
    class OptimizerResult(DCBase, ABC):
        """
        base class for all optimizer results

        :result:        actual optimization result
        :time:          time taken to solve the optimization
        :method:        method used to solve the optimization
        :optimizer:     the optimizer object that created this result
        """
        result: float
        time: float
        method: str = None
        optimizer: InitVar = None

        def __post_init__(self, optimizer=None):
            if not optimizer is None:
                assert issubclass(type(optimizer), OptimizerBase), f"optimizer must be a subclass of OptimizerBase {optimizer}"
            self._optimizer = optimizer
            # print("[OptimizerResult] post_init", optimizer)

        @property
        def optimizer(self):
            return self._optimizer

        def __float__(self):
            return float(self.result)

        # @property
        # def status(self):
        #     """problem status"""
        #     raise NotImplementedError("must be implemented in derived class")
        
        @abstractproperty
        def status(self):
            """problem status"""
            pass
        
        # @property
        # def is_error(self):
        #     """True if problem status is not OPTIMAL"""
        #     raise NotImplementedError("must be implemented in derived class")
        
        @abstractproperty
        def is_error(self):
            """True if problem status is not OPTIMAL"""
            pass

        # def detailed_error(self):
        #     """detailed error analysis"""
        #     raise NotImplementedError("must be implemented in derived class")

        @abstractproperty
        def detailed_error(self):
            """detailed error analysis"""
            pass
        
        @property
        def error(self):
            """problem error"""
            if not self.is_error:
                return None
            return self.detailed_error()

    @dataclass
    class SimpleResult(DCBase):
        result: float
        method: str = None
        errormsg: str = None
        context_dct: dict = None

        def __float__(self):
            if self.is_error:
                raise ValueError("cannot convert error result to float")
            return float(self.result)

        @property
        def is_error(self):
            return not self.errormsg is None

        @property
        def context(self):
            return self.context_dct if not self.context_dct is None else {}

    DERIVEPS = 1e-6

    @classmethod
    def deriv(cls, func, x):
        """
        computes the derivative of `func` at point `x`
        """
        h = cls.DERIVEPS
        return (func(x + h) - func(x - h)) / (2 * h)

    @classmethod
    def deriv2(cls, func, x):
        """
        computes the second derivative of `func` at point `x`
        """
        h = cls.DERIVEPS
        return (func(x + h) - 2 * func(x) + func(x - h)) / (h * h)

    @classmethod
    def findmin_gd(cls, func, x0, *, learning_rate=0.1, N=100):
        """
        finds the minimum of `func` using gradient descent starting at `x0`
        """
        x = x0
        for _ in range(N):
            x -= learning_rate * cls.deriv(func, x)
        return cls.SimpleResult(result=x, method="findmin_gd")

    @classmethod
    def findmax_gd(cls, func, x0, *, learning_rate=0.1, N=100):
        """
        finds the maximum of `func` using gradient descent, starting at `x0`
        """
        x = x0
        for _ in range(N):
            x += learning_rate * cls.deriv(func, x)
        return cls.SimpleResult(result=x, method="findmax_gd")

    @classmethod
    def findminmax_nr(cls, func, x0, *, N=20):
        """
        finds the minimum or maximum of func using Newton Raphson, starting at x0
        """
        x = x0
        for _ in range(N):
            # print("[NR]", x, func(x), cls.deriv(func, x), cls.deriv2(func, x))
            try:
                x -= cls.deriv(func, x) / cls.deriv2(func, x)
            except Exception as e:
                return cls.SimpleResult(
                    result=None,
                    errormsg=f"Newton Raphson failed: {e} [x={x}, x0={x0}]",
                    method="findminmax_nr",
                )
        return cls.SimpleResult(result=x, method="findminmax_nr")

    findmin = findminmax_nr
    findmax = findminmax_nr

    GOALSEEKEPS = 1e-6

    @classmethod
    def goalseek(cls, func, a, b):
        """
        finds the value of `x` where `func(x)` x is zero, using binary search between a,b
        """
        if func(a) * func(b) > 0:
            cls.SimpleResult(
                result=None,
                errormsg=f"function must have different signs at a,b [{a}, {b}, {func(a)} {func(b)}]",
                method="findminmax_nr",
            )
            raise ValueError("function must have different signs at a,b")
        while (b - a) > cls.GOALSEEKEPS:
            c = (a + b) / 2
            if func(c) == 0:
                return c
            elif func(a) * func(c) < 0:
                b = c
            else:
                a = c
        return cls.SimpleResult(result=(a + b) / 2, method="findminmax_nr")

    @staticmethod
    def posx(vector):
        """
        returns the positive elements of the vector, zeroes elsewhere
        """
        if isinstance(vector, np.ndarray):
            return np.maximum(0, vector)
        return tuple(max(0, x) for x in vector)

    @staticmethod
    def negx(vector):
        """
        returns the negative elements of the vector, zeroes elsewhere
        """
        if isinstance(vector, np.ndarray):
            return np.minimum(0, vector)
        return tuple(min(0, x) for x in vector)

    @staticmethod
    def a(vector):
        """helper: returns vector as np.array"""
        return np.array(vector)

    @staticmethod
    def t(vector):
        """helper: returns vector as tuple"""
        return tuple(vector)

    @staticmethod
    def F(func, rg):
        """helper: returns list of [func(x) for x in rg]"""
        return [func(x) for x in rg]

