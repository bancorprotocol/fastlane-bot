"""
Database manager object for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass, field, InitVar

import pandas as pd
import sqlalchemy
from sqlalchemy import MetaData, func
from sqlalchemy.orm import Session, sessionmaker

import fastlane_bot.db.models as models

from fastlane_bot.config import Config

from sqlalchemy_utils import database_exists, create_database

@dataclass
class DatabaseManagerBase:
    """
    Factory class for creating and managing pools.

    Parameters
    ----------
    session : Session
        The database session
    engine : sqlalchemy.engine
        The database engine
    metadata : MetaData
        The database metadata
    data : pd.DataFrame
        The dataframe containing the pools to add to the database
    backend_url : InitVar[str]
        The backend url to connect to

    """

    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"

    ConfigObj: Config

    session: Session = field(init=False)
    engine: sqlalchemy.engine = field(init=False)
    metadata: MetaData = field(init=False)
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    backend_url: InitVar[str] = None

    def __post_init__(self, backend_url=None):
        self.data = pd.read_csv(self.ConfigObj.DATABASE_SEED_FILE)
        self.data = self.data.sort_values("exchange", ascending=False)
        self.connect_db(backend_url=backend_url)

    @property
    def next_id(self) -> int:
        """
        Returns the next id
        """
        max_idx = self.session.query(func.max(getattr(models.Pool, 'id'))).first()[0]
        return max_idx + 1 if max_idx is not None else 0

    @property
    def next_cid(self) -> str:
        """
        Returns the next cid. The cid is a string representation of the next id,
        where id is assumed to be unique with respect to the Carbon strategy_id values bc they are huge numbers.
        """
        max_idx = self.session.query(func.max(getattr(models.Pool, 'id'))).first()[0]
        return str(max_idx + 1 if max_idx is not None else 0)

    def connect_db(self, *, backend_url=None):
        """
        Connects to the database. If the database does not exist, it creates it.
        """
        if backend_url is None:
            backend_url = self.ConfigObj.DEFAULT_DB_BACKEND_URL

        self.metadata = sqlalchemy.MetaData()
        
        # Check if the database exists, and create it if it doesn't
        if not database_exists(backend_url):
            create_database(backend_url)

        engine = sqlalchemy.create_engine(backend_url)
        models.mapper_registry.metadata.create_all(engine)
        sesh = sessionmaker(bind=engine)
        self.session = sesh()
        self.engine = engine

    def token_key_from_symbol_and_address(self, tkn_address: str, tkn_symbol: str) -> str:
        """
        Creates a token key from the token address and symbol. Uses "symbol-[last 4 characters of the address]".

        Parameters
        ----------
        tkn_address : str
            The address of the token
        tkn_symbol : str
            The symbol of the token

        Returns
        -------
        str
            The token key
        """
        return f"{tkn_symbol}-{tkn_address[-4:]}"

    def pair_name_from_token_keys(self, tkn0_key: int, tkn1_key: int) -> str:
        """
        Generates a pair name from the token keys

        Parameters
        ----------
        tkn0_key : int
            The key of the first token in the pair
        tkn1_key : int
            The key of the second token in the pair

        Returns
        -------
        str
            The pair name

        """
        return f"{tkn0_key}/{tkn1_key}"


