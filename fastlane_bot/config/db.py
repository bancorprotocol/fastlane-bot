"""
Fastlane bot config -- database configuration
"""
__VERSION__ = "1.0"
__DATE__ = "26/Apr 2023"
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
            return _ConfigDBPostgres(**kwargs)
        elif db == cls.DATABASE_SQLITE:
            return _ConfigDBSqlite(**kwargs)
        elif db == cls.DATABASE_MEMORY:
            return _ConfigDBMemory(**kwargs)
        elif db == cls.DATABASE_SDK:
            return _ConfigDBSdk(**kwargs)
        else:
            raise ValueError(f"Invalid db: {db}")
        
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

class _ConfigDBPostgres(ConfigDB):
    """
    Fastlane bot config -- database [Postgres]
    """
    db = S.DATABASE_POSTGRES    
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
            
class _ConfigDBSqlite(ConfigDB):
    """
    Fastlane bot config -- database [Sqlite]
    """
    SQLITE_URL = "sqlite:///fastlane_bot.db"
    #DEFAULT_DB_BACKEND_URL = POSTGRES_URL
    def __init__(self, **kwargs):
        raise NotImplementedError("Sqlite not implemented")
    
class _ConfigDBMemory(ConfigDB):
    """
    Fastlane bot config -- database [Memory]
    """
    def __init__(self, **kwargs):
        raise NotImplementedError("Memory not implemented")
    
class _ConfigDBSdk(ConfigDB):
    """
    Fastlane bot config -- database [SDK]
    """
    def __init__(self, **kwargs):
        raise NotImplementedError("SDK not implemented")