"""
[DOC-TODO-short description of what the file does, max 80 chars]

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import importlib.metadata

from .bot import CarbonBot as Bot, __VERSION__, __DATE__
from .config import Config, ConfigNetwork, ConfigDB, ConfigLogger, ConfigProvider


__version__ = importlib.metadata.version('fastlane-bot')
