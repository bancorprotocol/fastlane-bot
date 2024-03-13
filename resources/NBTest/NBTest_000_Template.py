# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# from fastlane_bot.config import Config
# print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))

from fastlane_bot.testing import *
# plt.style.use('seaborn-dark')
# plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)
# -

# # TEMPLATE [NBTest000]

# The section before the first `# ## Heading2` is for common code that is executed BEFORE the tests are run. It is rarely necessary to put code here.

MYVAR0 = 0

# ## Demo section [NOTEST]
#
# _this optional section is for demo purposes and it does not generate tests (inidcated by the trailing `[NOTEST`_
#
# - slow running not test relevant code SHOULD go here
# - code producing charts or code reading data not available in the testing environment MUST go here
# - any Heading 2 section can be market `[NOTEST]` regarding of location

pass

# ## Section 1
#
# This section will be converted to a function named `test_section_1()` therefore it is important to only have alphanumerics or underscore in the title.
#
# Note: Heading 3 and below are only decorative and should be used liberally.

# ### Using `iseq`
#
# `iseq` should be used for `float` comparisons; syntax is `iseq(a,b,c,...)` and they all must be equal to `a` for it not to fail.

assert m.sqrt(2) != 1.414213562373095
assert iseq(m.sqrt(2), 1.414213562373095)

# ### Using `raises`
#
# With raisese you can check whether a function call raises; eg to check if `f(a,b=b)` raises you do
#
#     assert raises(f, a, b=b) == <message>
#     

inv = lambda x: 1/x
assert inv(2) == 0.5
assert raises(inv, 0) == 'division by zero'

# ### Variable scope
#
# see next section

MYVAR1 = 1
assert MYVAR1 == 1
assert MYVAR0 == 0

# ## Section 2
#
# This is a new Heading two and therefor a new function, in this case called `test_section_2()`. Note the variables defined in a previous scope are not defined here.

myvar1 = lambda: MYVAR1

assert MYVAR0 == 0

# +
#myvar1() == 1 # ONLY True in the Notebook
# -

assert raises (myvar1) == "name 'MYVAR1' is not defined" # ONLY True in tests


