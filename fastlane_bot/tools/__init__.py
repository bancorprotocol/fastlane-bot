"""
FLB Tools -- Tools related to Bancor's Fastlane Bot.

---
(c) Copyright Bprotocol foundation 2023-24. 
Licensed under MIT
"""

__VERSION__ = '1.0+'
__VERSION_DATE__ = '07/Feb/2024'
__AUTHOR__ = 'Stefan K Loesch'
__COPYRIGHT__ = 'Bprotocol foundation 2023-24'
__LICENSE__ = 'MIT'


from .curves import SimplePair
Pair = SimplePair 
# TODO-RELEASE-202405: clean up Pair/SimplePair before final release

from .curves import CurveBase
from .curves import ConstantProductCurve
from .curves import CurveContainer

from .optimizer import MargPOptimizer
from .optimizer import PairOptimizer
