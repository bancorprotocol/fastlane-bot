"""
Fastlane bot config -- database configuration
"""
__VERSION__ = "1.0.1"
__DATE__ = "30/Apr 2023"
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
            self.POSTGRES_USER = "postgres"
        if not self.POSTGRES_PASSWORD:
            self.POSTGRES_PASSWORD = "postgres"
        if not self.POSTGRES_HOST:
            self.POSTGRES_HOST = "localhost"
        if not self.POSTGRES_DB:
            self.POSTGRES_DB = "postgres"
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
        raise NotImplementedError("Sqlite not implemented")
    
class _ConfigDBMemory(ConfigDB):
    """
    Fastlane bot config -- database [Memory]
    """
    DATABASE = S.DATABASE_MEMORY
    def __init__(self, **kwargs):
        raise NotImplementedError("Memory not implemented")
    
class _ConfigDBSdk(ConfigDB):
    """
    Fastlane bot config -- database [SDK]
    """
    DATABASE = S.DATABASE_SDK
    def __init__(self, **kwargs):
        raise NotImplementedError("SDK not implemented")