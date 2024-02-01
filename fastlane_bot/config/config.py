"""
Fastlane bot configuration object -- main object

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT
"""
from typing import Any

__VERSION__ = "1.0"
__DATE__ = "03/May 2023"

import os
from dataclasses import dataclass, field

from . import network as network_, db as db_, logger as logger_, provider as provider_
from .cloaker import CloakerL
from . import selectors as S
from dotenv import load_dotenv

load_dotenv()
TENDERLY_FORK_ID = os.environ.get("TENDERLY_FORK_ID")
if TENDERLY_FORK_ID is None:
    TENDERLY_FORK_ID = ""


@dataclass
class Config:
    """
    Fastlane bot configuration object
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    network: network_.ConfigNetwork = field(default=None)
    db: db_.ConfigDB = field(default=None)
    logger: logger_.ConfigLogger = field(default=None)
    provider: provider_.ConfigProvider = field(default=None)

    CONFIG_UNITTEST = "unittest"
    CONFIG_TENDERLY = "tenderly"
    CONFIG_MAINNET = "mainnet"

    LOGLEVEL_DEBUG = S.LOGLEVEL_DEBUG
    LOGLEVEL_INFO = S.LOGLEVEL_INFO
    LOGLEVEL_WARNING = S.LOGLEVEL_WARNING
    LOGLEVEL_ERROR = S.LOGLEVEL_ERROR

    LL_DEBUG = S.LOGLEVEL_DEBUG
    LL_INFO = S.LOGLEVEL_INFO
    LL_WARN = S.LOGLEVEL_WARNING
    LL_ERR = S.LOGLEVEL_ERROR

    SUPPORTED_EXCHANGES = [
        "carbon_v1",
        "bancor_v2",
        "bancor_v3",
        "uniswap_v2",
        "uniswap_v3",
        "sushiswap_v2",
        "bancor_pol",
        "pancakeswap_v2",
        "pancakeswap_v3",
    ]

    logging_header: str = None

    @classmethod
    def new(
        cls,
        *,
        config=None,
        loglevel=None,
        logging_path=None,
        blockchain=None,
        self_fund=True,
        **kwargs,
    ) -> "Config":
        """
        Fastlane bot configuration object -- main object

        Args:
            config: The configuration type. Defaults to None.
            loglevel: The log level. Defaults to None.
            logging_path: The logging path. Defaults to None.
            blockchain: The blockchain network. Defaults to None.
            self_fund: Whether to self fund. Defaults to True.
            **kwargs: Additional keyword arguments.

        Returns:
            Config: The Config object.

        Raises:
            ValueError: If the config is invalid.

        Examples:
            # Create a new Config object
            config = Config.new(config="mainnet", loglevel="info", logging_path="/path/to/logs")
        """

        if config is None:
            config = cls.CONFIG_MAINNET

        if loglevel is None:
            loglevel = cls.LOGLEVEL_INFO

        C_log = logger_.ConfigLogger.new(loglevel=loglevel, logging_path=logging_path)

        if config == cls.CONFIG_MAINNET:
            C_nw = network_.ConfigNetwork.new(network=blockchain)
            C_nw.SELF_FUND = self_fund
            return cls(network=C_nw, logger=C_log, **kwargs)
        elif config == cls.CONFIG_TENDERLY:
            C_db = db_.ConfigDB.new(db=S.DATABASE_POSTGRES, POSTGRES_DB="tenderly")
            C_nw = network_.ConfigNetwork.new(network=S.NETWORK_TENDERLY)
            C_nw.SELF_FUND = self_fund
            return cls(db=C_db, logger=C_log, network=C_nw, **kwargs)
        elif config == cls.CONFIG_UNITTEST:
            C_db = db_.ConfigDB.new(db=S.DATABASE_UNITTEST, POSTGRES_DB="unittest")
            C_nw = network_.ConfigNetwork.new(network=S.NETWORK_MAINNET)
            C_nw.SELF_FUND = self_fund
            C_pr = provider_.ConfigProvider.new(
                network=C_nw, provider=S.PROVIDER_DEFAULT
            )
            return cls(db=C_db, logger=C_log, network=C_nw, provider=C_pr, **kwargs)
        raise ValueError(f"Invalid config: {config}")

    def is_config_item(self, item: str) -> bool:
        """
        Checks if an item is a valid configuration item.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is a valid configuration item, False otherwise.
        """

        if item in {"w3", "connection", "w3_async"}:
            return True
        if len(item) < 3:
            return False
        if not item[0].isupper():
            return False
        for c in item[1:]:
            if not (item.isupper() or item.isnumeric() or item == "_"):
                return False
        return True

    def get_attribute_from_config(self, name: str) -> Any:
        """
        Gets the attribute from the constituent config objects.

        Args:
            name: The name of the attribute to retrieve.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute is not found in any of the config objects.
        """
        for obj in [self.network, self.db, self.provider, self.logger]:
            if hasattr(obj, name):
                return getattr(obj, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __getattr__(self, name: str) -> Any:
        """
        Gets the attribute dynamically from the config objects.

        Args:
            name: The name of the attribute to retrieve.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute is not found in any of the config objects.
        """
        if self.is_config_item(name):
            return self.get_attribute_from_config(name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __post_init__(self) -> None:
        """
        Performs post-initialization initialization.

        Raises:
            AssertionError: If the network, db, logger, or provider objects are not of the expected types or if there is a network mismatch.
        """
        if self.network is None:
            self.network = network_.ConfigNetwork.new(
                network_.ConfigNetwork.NETWORK_ETHEREUM
            )
        assert issubclass(type(self.network), network_.ConfigNetwork)

        if self.db is None:
            self.db = db_.ConfigDB.new(db_.ConfigDB.DATABASE_POSTGRES)
        assert issubclass(type(self.db), db_.ConfigDB)

        if self.logger is None:
            self.logger = logger_.ConfigLogger.new()
        assert issubclass(type(self.logger), logger_.ConfigLogger)

        if self.provider is None:
            self.provider = provider_.ConfigProvider.new(self.network)
        assert issubclass(type(self.provider), provider_.ConfigProvider)

        assert (
            self.network is self.provider.network
        ), f"Network mismatch: {self.network} != {self.provider.network}"
        self.SUPPORTED_EXCHANGES = self.network.ALL_KNOWN_EXCHANGES

    VISIBLE_FIELDS = "network, db, logger, provider, w3, ZERO_ADDRESS"

    def cloaked(self, incl=None, excl=None):
        """
        Returns a cloaked version of the object.

        Args:
            incl: Fields to include in the cloaked version (in addition to those in VISIBLE_FIELDS). Defaults to None.
            excl: Fields to exclude from the cloaked version. Defaults to None.

        Returns:
            CloakerL: The cloaked version of the object.
        """
        visible = self.VISIBLE_FIELDS
        if isinstance(visible, str):
            visible = (x.strip() for x in visible.split(","))
        visible = set(visible)

        if isinstance(incl, str):
            incl = (x.strip() for x in incl.split(","))
        elif incl is None:
            incl = []
        visible |= set(incl)

        if isinstance(excl, str):
            excl = (x.strip() for x in excl.split(","))
        elif excl is None:
            excl = []
        visible -= set(excl)

        return CloakerL(self, visible)
