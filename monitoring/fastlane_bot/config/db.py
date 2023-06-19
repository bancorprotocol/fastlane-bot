"""
Fastlane bot config -- database configuration
"""
__VERSION__ = "1.0.4"
__DATE__ = "01/May 2023"
from .base import ConfigBase
from . import selectors as S

import os
from dotenv import load_dotenv
load_dotenv()



class ConfigDB(ConfigBase):
    """
    Fastlane bot config -- database
    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    _PROJECT_PATH = os.path.normpath(f"{os.getcwd()}") # TODO: FIX THIS
    
    DATABASE_SEED_FILE = os.path.normpath(
        f"{_PROJECT_PATH}/fastlane_bot/data/seed_token_pairs.csv"
    )
    
    
    DATABASE_SQLITE = S.DATABASE_SQLITE
    DATABASE_POSTGRES = S.DATABASE_POSTGRES
    DATABASE_MEMORY = S.DATABASE_MEMORY
    DATABASE_SDK = S.DATABASE_SDK
    DATABASE_UNITTEST = S.DATABASE_UNITTEST
    @classmethod
    def new(cls, db=None, **kwargs):
        """
        Return a new ConfigDB object for the specified database.
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
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class _ConfigDBPostgres(ConfigDB):
    """
    Fastlane bot config -- database [Postgres]
    """
    DATABASE = S.DATABASE_POSTGRES    
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_URL = None # set in init
    
    POSTGRES_USER_DEFAULT = "postgres"
    POSTGRES_PASSWORD_DEFAULT = "postgres"
    POSTGRES_HOST_DEFAULT = "localhost"
    POSTGRES_DATABASE_DEFAULT = "mainnet"

    def __init__(self, **kwargs):
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
    Fastlane bot config -- database [Sqlite]
    """
    DATABASE = S.DATABASE_SQLITE
    SQLITE_URL = "sqlite:///fastlane_bot.db"
    #DEFAULT_DB_BACKEND_URL = POSTGRES_URL
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise NotImplementedError("Sqlite not implemented")

class _ConfigDBUnittest(ConfigDB):
    """
    Fastlane bot config -- database [Postgres]
    """
    DATABASE = S.DATABASE_UNITTEST

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
class _ConfigDBMemory(ConfigDB):
    """
    Fastlane bot config -- database [Memory]
    """
    DATABASE = S.DATABASE_MEMORY
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise NotImplementedError("Memory not implemented")

    
class _ConfigDBSdk(ConfigDB):
    """
    Fastlane bot config -- database [SDK]
    """
    DATABASE = S.DATABASE_SDK
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise NotImplementedError("SDK not implemented")

class _ConfigDBUnitTest(ConfigDB):
    """
    Fastlane bot config -- database [UnitTest]
    """
    DATABASE = S.DATABASE_UNITTEST
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_URL = None # set in init

    POSTGRES_USER_DEFAULT = "postgres"
    POSTGRES_PASSWORD_DEFAULT = "postgres"
    POSTGRES_HOST_DEFAULT = "localhost"
    POSTGRES_DATABASE_DEFAULT = "unittest"
    def __init__(self, **kwargs):
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
    