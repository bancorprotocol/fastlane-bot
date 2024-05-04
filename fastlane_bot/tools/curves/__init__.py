"""
bonding curve management and analysis

---
(c) Copyright Bprotocol foundation 2023-24. 
Licensed under MIT
"""
from .simplepair import SimplePair
Pair = SimplePair
# TODO-RELEASE-202405: clean up Pair/SimplePair before final release

from .curvebase import CurveBase
from .curvebase import AttrDict
from .cpc import ConstantProductCurve
from .cpc import T
from .curvecontainer import CurveContainer
from .cpcinverter import CPCInverter

