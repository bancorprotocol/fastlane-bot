# ------------------------------------------------------------
# Auto generated test file `test_007_NoneResult.py`
# ------------------------------------------------------------
# source file   = NBTest_007_NoneResult.py
# test id       = 007
# test comment  = NoneResult
# ------------------------------------------------------------



#from fastlane_bot import Bot, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.noneresult import NoneResult, isNone
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(NoneResult))
from fastlane_bot.testing import *
import itertools as it
import collections as cl
import math as m
#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)




# ------------------------------------------------------------
# Test      007
# File      test_007_NoneResult.py
# Segment   NoneResult Basics
# ------------------------------------------------------------
def test_noneresult_basics():
# ------------------------------------------------------------
    
    none = NoneResult()
    assert str(none) == "NoneResult('None')"
    assert repr(none) == str(none)
    assert bool(none) == False
    assert float(none) == 0.0
    assert int(none) == 0 
    assert m.floor(none) is none
    assert m.ceil(none) is none
    assert m.trunc(none) is none
    assert round(none,5) is none
    assert None == none
    
    assert none.foo is none
    assert none.foo.bar is none
    assert none["foo"] is none
    assert none["foo"]["bar"] is none
    
    assert none+1 is none
    assert none-1 is none
    assert none*1 is none
    assert none/1 is none
    assert none//1 is none
    assert none**1 is none
    assert none%1 is none
    
    assert 1+none is none
    assert 1-none is none
    assert 1*none is none
    assert 1/none is none
    assert 1//none is none
    assert 1**none is none
    assert 1%none is none
    
    none_foo = NoneResult("foo")
    assert str(none_foo) == "NoneResult('foo')"
    assert none_foo == none
    

# ------------------------------------------------------------
# Test      007
# File      test_007_NoneResult.py
# Segment   None format
# ------------------------------------------------------------
def test_none_format():
# ------------------------------------------------------------
    
    none = NoneResult()
    assert f"{none}" == "NoneResult('None')"
    assert "{}".format(none) == "NoneResult('None')"
    
    assert f":{str(none):30}:" == ":NoneResult('None')            :"
    assert f":{none:30}:" == f":{str(none):30}:"
    assert len(f"{none:30}") == 30
    raises(lambda: f"{none:2.1f}") == "Unknown format code 'f' for object of type 'str'"
    assert f"{float(none):10.4f}" == '    0.0000'
    assert f"{int(none):010d}" == '0000000000'
    
    a="123"
    
    f"{none:40}"
    

# ------------------------------------------------------------
# Test      007
# File      test_007_NoneResult.py
# Segment   math functions
# ------------------------------------------------------------
def test_math_functions():
# ------------------------------------------------------------
    
    none = NoneResult()
    assert m.sin(none) == 0
    assert m.cos(none) == 1
    assert m.exp(none) == 1
    assert raises(m.log, none) == "math domain error"
    assert 1/none == none
    assert 0*none==none
    sin = lambda x: 0*x+m.sin(x)
    assert sin(none) == none
    

# ------------------------------------------------------------
# Test      007
# File      test_007_NoneResult.py
# Segment   isNone
# ------------------------------------------------------------
def test_isnone():
# ------------------------------------------------------------
    
    assert isNone(None) == True
    assert isNone(NoneResult()) == True
    assert isNone(NoneResult("moo")) == True
    assert isNone(0) == False
    assert isNone("") == False
    assert isNone(False) == False
    assert isNone(NoneResult) == False
    
    none = NoneResult()
    assert raises(lambda x: isNone(None+x), 1) == "unsupported operand type(s) for +: 'NoneType' and 'int'"
    assert isNone(none+1)
    assert isNone(1+none)
    assert isNone(none**2)
    assert isNone(none*none)
    assert isNone(1+2*none+3*none*none)
    
    assert not isNone(none) == False
    assert [x for x in (1,2,None,3) if not isNone(x)] == [1,2,3]
    assert [x for x in (1,2,none,3) if not isNone(x)] == [1,2,3]
    assert [2*x for x in (1,2,None,3) if not isNone(x)] == [2,4,6]
    assert [2*x for x in (1,2,none,3) if not isNone(x)] == [2,4,6]
    assert [2*x for x in (1,2,none,3) if not isNone(2*x)] == [2,4,6]
    
    
    
    