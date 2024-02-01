"""
Fastlane bot config -- database configuration

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT
"""
from typing import Optional

__VERSION__ = "1.0.4"
__DATE__ = "01/May 2023"

from .base import ConfigBase
from . import selectors as S

import os
from dotenv import load_dotenv

load_dotenv()


class ConfigDB(ConfigBase):
    """
    Database configuration class.

    Explanation:
        This class represents the configuration for a database. It inherits from the ConfigBase class and provides additional attributes and methods specific to database configuration.

    Attributes:
        __VERSION__: The version of the database configuration.
        __DATE__: The date of the database configuration.
        _PROJECT_PATH: The path of the project.
        DATABASE_SEED_FILE: The path of the seed token pairs file.
        DATABASE_SQLITE: The SQLite database type.
        DATABASE_POSTGRES: The PostgreSQL database type.
        DATABASE_MEMORY: The in-memory database type.
        DATABASE_SDK: The SDK database type.
        DATABASE_UNITTEST: The unit test database type.

    Methods:
        new: Create a new ConfigDB object for the specified database.

    Args:
        db: The type of the database. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        ConfigDB: The ConfigDB object for the specified database.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    _PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")  # TODO: FIX THIS

    DATABASE_SEED_FILE = os.path.normpath(
        f"{_PROJECT_PATH}/fastlane_bot/data/seed_token_pairs.csv"
    )

    DATABASE_SQLITE = S.DATABASE_SQLITE
    DATABASE_POSTGRES = S.DATABASE_POSTGRES
    DATABASE_MEMORY = S.DATABASE_MEMORY
    DATABASE_SDK = S.DATABASE_SDK
    DATABASE_UNITTEST = S.DATABASE_UNITTEST

    @classmethod
    def new(cls, db: Optional[str] = None, **kwargs) -> "_ConfigDBPostgres":
        """
        Creates a new ConfigDB object for the specified database.

        Args:
            db: The type of the database. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            ConfigDB: The ConfigDB object for the specified database.

        Raises:
            ValueError: If the specified database type is invalid.
        """

        if db is None:
            db = cls.DATABASE_POSTGRES
        if db == cls.DATABASE_POSTGRES:
            return _ConfigDBPostgres(_direct=False, **kwargs)
        elif db == cls.DATABASE_SQLITE:
            return _ConfigDBSqlite(_direct=False, **kwargs)
        elif db == cls.DATABASE_MEMORY:
            return _ConfigDBMemory(_direct=False, **kwargs)
        elif db == cls.DATABASE_SDK:
            return _ConfigDBSdk(_direct=False, **kwargs)
        elif db == cls.DATABASE_UNITTEST:
            return _ConfigDBUnitTest(_direct=False, **kwargs)
        else:
            raise ValueError(f"Invalid db: {db}")

    def __init__(self, **kwargs) -> None:
        """
        Initializes the ConfigDB object.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        super().__init__(**kwargs)


class _ConfigDBPostgres(ConfigDB):
    """
    PostgreSQL database configuration class.

    Explanation:
        This class represents the configuration for a PostgreSQL database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to PostgreSQL.

    Attributes:
        DATABASE: The type of the database.
        POSTGRES_USER: The username for the PostgreSQL database.
        POSTGRES_PASSWORD: The password for the PostgreSQL database.
        POSTGRES_HOST: The host for the PostgreSQL database.
        POSTGRES_DB: The name of the PostgreSQL database.
        POSTGRES_URL: The URL for the PostgreSQL database.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """

    DATABASE = S.DATABASE_POSTGRES
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_URL = None  # set in init
    POSTGRES_USER_DEFAULT = "postgres"
    POSTGRES_PASSWORD_DEFAULT = "postgres"
    POSTGRES_HOST_DEFAULT = "localhost"
    POSTGRES_DATABASE_DEFAULT = "mainnet"

    def __init__(self, **kwargs) -> None:
        """
        Initializes the ConfigDBPostgres object.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        super().__init__(**kwargs)
        if not self.POSTGRES_URL is None:
            # those are all set to None if URL is given
            self.POSTGRES_USER = None
            self.POSTGRES_PASSWORD = None
            self.POSTGRES_HOST = None
            self.POSTGRES_DB = None
            return

        if not self.POSTGRES_USER:
            self.POSTGRES_USER = self.POSTGRES_USER_DEFAULT
        if not self.POSTGRES_PASSWORD:
            self.POSTGRES_PASSWORD = self.POSTGRES_PASSWORD_DEFAULT
        if not self.POSTGRES_HOST:
            self.POSTGRES_HOST = self.POSTGRES_HOST_DEFAULT
        if not self.POSTGRES_DB:
            self.POSTGRES_DB = self.POSTGRES_DATABASE_DEFAULT
        self.POSTGRES_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        self.DEFAULT_DB_BACKEND_URL = self.POSTGRES_URL


class _ConfigDBSqlite(ConfigDB):
    """
    Sqlite database configuration class.

    Explanation:
        This class represents the configuration for a Sqlite database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to Sqlite.

    Attributes:
        DATABASE: The type of the database.
        SQLITE_URL: The URL for the Sqlite database.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        NotImplementedError: If Sqlite is not implemented.
    """

    DATABASE = S.DATABASE_SQLITE
    SQLITE_URL = "sqlite:///fastlane_bot.db"

    # DEFAULT_DB_BACKEND_URL = POSTGRES_URL
    def __init__(self, **kwargs):
        """
        Initializes the ConfigDBSqlite object.

        Raises:
            NotImplementedError: If Sqlite is not implemented.
        """

        super().__init__(**kwargs)
        raise NotImplementedError("Sqlite not implemented")


class _ConfigDBUnittest(ConfigDB):
    """
    Unittest database configuration class.

    Explanation:
        This class represents the configuration for a unittest database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to the unittest database.

    Attributes:
        DATABASE: The type of the database.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """

    DATABASE = S.DATABASE_UNITTEST

    def __init__(self, **kwargs):
        """
        Initializes the ConfigDB object.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        super().__init__(**kwargs)


class _ConfigDBMemory(ConfigDB):
    """
    Memory database configuration class.

    Explanation:
        This class represents the configuration for a memory database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to memory.

    Attributes:
        DATABASE: The type of the database.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        NotImplementedError: If memory is not implemented.
    """

    DATABASE = S.DATABASE_MEMORY

    def __init__(self, **kwargs):
        """
        Initializes the ConfigDBMemory object.

        Raises:
            NotImplementedError: If memory is not implemented.
        """

        super().__init__(**kwargs)
        raise NotImplementedError("Memory not implemented")


class _ConfigDBSdk(ConfigDB):
    """
    SDK database configuration class.

    Explanation:
        This class represents the configuration for an SDK database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to the SDK database.

    Attributes:
        DATABASE: The type of the database.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        NotImplementedError: If SDK is not implemented.
    """

    DATABASE = S.DATABASE_SDK

    def __init__(self, **kwargs):
        """
        SDK database configuration class.

        Explanation:
            This class represents the configuration for an SDK database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to the SDK database.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None

        Raises:
            NotImplementedError: If the SDK is not implemented.
        """

        super().__init__(**kwargs)
        raise NotImplementedError("SDK not implemented")


class _ConfigDBUnitTest(ConfigDB):
    """
    Unittest database configuration class.

    Explanation:
        This class represents the configuration for a unittest database. It inherits from the ConfigDB class and provides additional attributes and initialization logic specific to the unittest database.

    Attributes:
        DATABASE: The type of the database.
        POSTGRES_USER: The username for the PostgreSQL database.
        POSTGRES_PASSWORD: The password for the PostgreSQL database.
        POSTGRES_HOST: The host for the PostgreSQL database.
        POSTGRES_DB: The name of the PostgreSQL database.
        POSTGRES_URL: The URL for the PostgreSQL database.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """

    DATABASE = S.DATABASE_UNITTEST
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_URL = None  # set in init

    POSTGRES_USER_DEFAULT = "postgres"
    POSTGRES_PASSWORD_DEFAULT = "postgres"
    POSTGRES_HOST_DEFAULT = "localhost"
    POSTGRES_DATABASE_DEFAULT = "unittest"

    def __init__(self, **kwargs):
        """
        Initializes the ConfigDB object.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        super().__init__(**kwargs)

        if not self.POSTGRES_URL is None:
            # those are all set to None if URL is given
            self.POSTGRES_USER = None
            self.POSTGRES_PASSWORD = None
            self.POSTGRES_HOST = None
            self.POSTGRES_DB = None
            return

        if not self.POSTGRES_USER:
            self.POSTGRES_USER = self.POSTGRES_USER_DEFAULT
        if not self.POSTGRES_PASSWORD:
            self.POSTGRES_PASSWORD = self.POSTGRES_PASSWORD_DEFAULT
        if not self.POSTGRES_HOST:
            self.POSTGRES_HOST = self.POSTGRES_HOST_DEFAULT
        if not self.POSTGRES_DB:
            self.POSTGRES_DB = self.POSTGRES_DATABASE_DEFAULT
        self.POSTGRES_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        self.DEFAULT_DB_BACKEND_URL = self.POSTGRES_URL
