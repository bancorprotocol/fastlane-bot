# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
try:
    import tools.invariants.vector as dv
    from testing import *
except:
    import fastlane_bot.tools.invariants.vector as dv
    from fastlane_bot.testing import *

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(dv.DictVector))
# -

# # Dict Vectors (Invariants Module)

# ## Basic dict vector functions

vec1 = dict(a=1, b=2)
vec2 = dict(b=3, c=4)
vec3 = dict(c=1, a=3)

assert iseq(dv.norm(vec1)**2, 1+4)
assert iseq(dv.norm(vec2)**2, 9+16)
assert iseq(dv.norm(vec3)**2, 1+9)
assert iseq(dv.norm(vec1)**2, dv.sprod(vec1, vec1))
assert iseq(dv.norm(vec2)**2, dv.sprod(vec2, vec2))
assert iseq(dv.norm(vec3)**2, dv.sprod(vec3, vec3))

assert dv.eq(vec1, vec1)
assert dv.eq(vec2, vec2)
assert dv.eq(vec3, vec3)
assert not dv.eq(vec1, vec2)
assert not dv.eq(vec3, vec2)
assert not dv.eq(vec1, vec3)

assert dv.add(vec1, vec2) == dict(a=1, b=5, c=4)
assert dv.add(vec1, vec3) == dict(a=4, b=2, c=1)
assert dv.add(vec2, vec3) == dict(a=3, b=3, c=5)
assert dv.add(vec1, vec2) == dv.add(vec2, vec1)
assert dv.add(vec1, vec3) == dv.add(vec3, vec1)
assert dv.add(vec2, vec3) == dv.add(vec3, vec2)

assert dv.add(vec1, vec1) == dv.smul(vec1, 2)
assert dv.add(vec2, vec2) == dv.smul(vec2, 2)
assert dv.add(vec3, vec3) == dv.smul(vec3, 2)

assert dv.DictVector.dict_add == dv.add
assert dv.DictVector.dict_sub == dv.sub
assert dv.DictVector.dict_smul == dv.smul
assert dv.DictVector.dict_sprod == dv.sprod
assert dv.DictVector.dict_norm == dv.norm
assert dv.DictVector.dict_eq == dv.eq

# ## DictVector object

# null vector

# +
vec0 = dv.DictVector.null()
vec0a = dv.DictVector()
vec0b = dv.DictVector.n(a=0, b=0, x=0)

assert bool(vec0) is False
assert bool(vec0a) is False
assert bool(vec0b) is False
assert vec0 == vec0a
assert vec0 == vec0b
assert vec0a == vec0b
assert len(vec0) == 0
assert len(vec0a) == 0
assert len(vec0b) == 0
assert vec0.norm == 0
assert vec0a.norm == 0
assert vec0b.norm == 0
assert not "a" in vec0
assert not "a" in vec0a
assert not "a" in vec0b
vec0, vec0b
# -

# non-null vector

vec1 = dv.DictVector.n(a=1, b=2, x=0)
vec1b = dv.DictVector(vec1.vec)
assert bool(vec1) is True
assert bool(vec1b) is True
assert vec1["a"] == 1
assert vec1["b"] == 2
assert vec1["c"] == 0 # !!! <<== missing elements are 0!
assert vec1["x"] == 0
assert "a" in vec1
assert "b" in vec1
assert not "c" in vec1
assert not "x" in vec1
assert vec1 == vec1b
vec1

# various ways of creating a vector

veca = dv.DictVector(dict(a=1, b=2, x=0))
vecb = dv.DictVector.new(a=1, b=2, x=0)
vecc = dv.DictVector.new(dict(a=1, b=2, x=0))
vecd = dv.DictVector.n(a=1, b=2, x=0)
vece = dv.DictVector.n(dict(a=1, b=2, x=0))
vecf = dv.V(a=1, b=2, x=0)
vecg = dv.V(dict(a=1, b=2, x=0))
assert veca == vecb
assert veca == vecc
assert veca == vecd
assert veca == vece
assert veca == vecf
assert veca == vecg

# vector arithmetic

assert vec0 + vec1 == vec1
assert vec0b + vec1 == vec1
assert vec1 + vec1 == 2*vec1
assert vec1 + vec1 == vec1*2
assert 3*vec1 == vec1*3
assert +vec1 == vec1
assert -vec1 == vec1 * (-1)
assert -vec1 == -1 * vec1
assert bool(0*vec1) is False
assert 0*vec1 == vec0
assert 0*vec1 == vec0b
assert 0*vec1 == vec1*0
assert (0*vec1).norm == 0
assert 2*3*vec1 == 6*vec1
assert 2*vec1*3 == vec1*6
assert 2*3*vec1/6 == vec1

# vector base

# +
labels = "abcdefghijklmnop"
base = {l:dv.DictVector({l:1})for l in labels}
for x in base.values():
    for y in base.values():
        if x == y:
            #print(x,y,x*y)
            assert x*y == 1
        else:
            assert x*y == 0
            
assert base["a"] * dv.V(a=1, b=2) == 1
assert base["b"] * dv.V(a=1, b=2) == 2
assert base["c"] * dv.V(a=1, b=2) == 0
assert base["a"]+2*base["b"] == dv.V(a=1, b=2)
# -

# floor / ceil / round / abs

vec2 = dv.V(a=1.2345, b=9.8765, c=3.5, d=1)
assert m.floor(vec2) == dv.V(a=1, b=9, c=3, d=1)
assert m.ceil(vec2) == dv.V(a=2, b=10, c=4, d=1)
assert m.ceil(vec2) - m.floor(vec2) == dv.V(a=1, b=1, c=1)
assert round(vec2) == dv.V(a=1, b=10, c=4, d=1)
assert round(vec2, 1) == dv.V(a=1.2, b=9.9, c=3.5, d=1)
assert abs(vec2) == vec2
assert abs(-vec2) == vec2

# incremental actions

v = dv.V()
assert not v
v += dv.V(a=1, b=2)
assert v
assert v == dv.V(a=1, b=2)
v *= 2
assert v == 2*dv.V(a=1, b=2)
v += dv.V(a=3, c=3)
assert v == dv.V(a=5, b=4, c=3)
v /= 2
assert v == 0.5 * dv.V(a=5, b=4, c=3)
v -= v
assert bool(v) is False
assert not v
v


# generic base vector 

# +
class Foo():
    pass

@dv.dataclass(frozen=True)
class Bar():
    val: str
    
foo1 = Foo()
foo2 = Foo()
assert foo1 != foo2

bar1  = Bar("bang")
bar1a = Bar("bang")
assert bar1 == bar1a
assert not bar1 is bar1a

va = dv.V({foo1: 3, foo2:4})
assert len(va) == 2
assert va.norm == 5

va = dv.V({bar1: 3, foo1:4})
assert len(va) == 2
assert va.norm == 5

va = dv.V({bar1: 3, bar1a:4})
assert len(va) == 1
assert va.norm == 4

va = dv.V({bar1: 3})
vb = dv.V({bar1a: 3})
assert va == vb
assert not va is vb
# -


