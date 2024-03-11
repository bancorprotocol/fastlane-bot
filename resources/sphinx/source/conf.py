# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'FLBTools'
copyright = '2023-24, Bprotocol foundation'
author = 'Stefan K Loesch'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'autodoc_preprocess_topazeblue',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'custom.css',
]

# -- Custom variables --------------------------------------------------------

import tools
version = tools.__VERSION__
release = version
date = tools.__VERSION_DATE__
author = tools.__AUTHOR__
copyright = tools.__COPYRIGHT__

import tools.cpc
import tools.invariants
from tools.optimizer import *
margp_optimizer_vd = f"v{MargPOptimizer.__VERSION__} ({MargPOptimizer.__DATE__})"
optimizer_base_vd = f"v{OptimizerBase.__VERSION__} ({OptimizerBase.__DATE__})"
cpcarb_optimizer_vd = f"v{PairOptimizer.__VERSION__} ({PairOptimizer.__DATE__})"
convex_optimizer_vd = f"v{ConvexOptimizer.__VERSION__} ({ConvexOptimizer.__DATE__})"
pair_optimizer_vd = f"v{PairOptimizer.__VERSION__} ({PairOptimizer.__DATE__})"

from tools.cpc import ConstantProductCurve, CPCContainer
#from tools.cpcbase import CurveBase
cpc_vd = f"v{ConstantProductCurve.__VERSION__} ({ConstantProductCurve.__DATE__})"
cpc_container_vd = f"v{CPCContainer.__VERSION__} ({CPCContainer.__DATE__})"
#curve_base_vd = f"v{CurveBase.__VERSION__} ({CurveBase.__DATE__})"



# conf.py
rst_epilog = f"""
.. |date| replace:: {date}
.. |author| replace:: {author}
.. |copyright| replace:: {copyright}
.. |margp_optimizer_vd| replace:: {margp_optimizer_vd}
.. |pair_optimizer_vd| replace:: {pair_optimizer_vd}
.. |convex_optimizer_vd| replace:: {convex_optimizer_vd}
.. |cpcarb_optimizer_vd| replace:: {cpcarb_optimizer_vd}
.. |optimizer_base_vd| replace:: {optimizer_base_vd}
.. |cpc_vd| replace:: {cpc_vd}
.. |cpc_container_vd| replace:: {cpc_container_vd}
"""
#.. |xxx_optimizer_vd| replace:: {xxx_optimizer_vd}


