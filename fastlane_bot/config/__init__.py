"""
Configuration-related classes

The classes into this module are

- ``ConfigBase`` (``base``; base class)
    - ``ConfigNetwork`` (``network``; network/chain)
    - ``ConfigDB`` (``db``; database) -- DEPRECATED?
    - ``ConfigLogger`` (``logger``; logging)
    - ``ConfigProvider`` (``provider``; provider for network access) 
- ``Config`` (``config``; main configuration class, integrates the above)

Submodules provide the following

- Constants (``constants`` and ``selectors``; various constants)
- ``MultiCaller`` and related (``multicaller``; TODO: what is this?)
- ``NetworkBase`` and ``EthereumNetwork`` (``connect``; network/chain connection code TODO: details)
- ``Cloaker`` (``cloaker``; deprecated)



---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
# from . import network, base, config, db, selectors, cloaker

from .network import ConfigNetwork
from .db import ConfigDB
from .logger import ConfigLogger
from .provider import ConfigProvider

from .config import Config
