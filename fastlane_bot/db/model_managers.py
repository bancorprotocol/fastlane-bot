"""
Table managers of the Fastlane project..

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, Type
from typing import List, Optional, Union

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

import fastlane_bot.db.models as models
from fastlane_bot.db.manager_base import DatabaseManagerBase
from fastlane_bot.db.models import Pool, Pair


@dataclass
class TokenManager(DatabaseManagerBase):
    """
    A class to manage CRUD operations for the Token model.

    Methods
    -------
    create_token(token: Token) -> Optional[Token]
        Create a new token.
    get_token(**kwargs) -> Optional[Token]
        Get a token by its attributes.
    get_tokens(**kwargs) -> List[Token]
        Get a list of tokens by their attributes.
    update_token(token: Token) -> Optional[Token]
        Update a token.
    delete_token(token: Token) -> Optional[Token]
        Delete a token.

    """

    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"

    def create_token(self, token: models.Token) -> Optional[models.Token]:
        """
        Create a new token.

        Parameters
        ----------
        token : Token
            The token object to add to the database.

        Returns
        -------
        Optional[Token]
            The created token object, or None if an error occurs.
        """
        try:
            self.session.add(token)
            self.session.commit()
            return token
        except IntegrityError:
            self.session.rollback()
            return None

    def get_token(self, **kwargs) -> Optional[models.Token]:
        """
        Get a token by its attributes.

        Parameters
        ----------
        **kwargs
            The attributes of the token to search for.

        Returns
        -------
        Optional[Token]
            The retrieved token object, or None if not found.
        """
        return self.session.query(models.Token).filter_by(**kwargs).first()

    def get_tokens(self) -> List[Type[models.Token]]:
        """
        Get all tokens in the database.

        Returns
        -------
        List[Token]
            A list of all token objects.
        """
        return self.session.query(models.Token).all()

    def update_token(self, token: models.Token, new_data: Dict[str, Any]) -> Optional[models.Token]:
        """
        Update an existing token object.

        Parameters
        ----------
        token : Token
            The token object to update.
        new_data : Dict[str, Any]
            A dictionary containing the attributes to update.

        Returns
        -------
        Optional[Token]
            The updated token object, or None if an error occurs.
        """
        try:
            for key, value in new_data.items():
                setattr(token, key, value)
            self.session.commit()
            return token
        except IntegrityError:
            self.session.rollback()
            return None

    def delete_token(self, token: models.Token) -> bool:
        """
        Delete a token object.

        Parameters
        ----------
        token : Token
            The token object to delete.

        Returns
        -------
        bool
            True if the token is deleted, False if an error occurs.
        """
        try:
            self.session.delete(token)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            return False




@dataclass
class PairManager(DatabaseManagerBase):
    """
    A class to manage CRUD operations for the Pair model.

    Methods
    -------
    create_pair(pair: Pair) -> Union[Pair, None]
        Create a new pair in the database.
    get_pair(**kwargs) -> Union[Pair, None]
        Get a pair by its attributes.
    get_pairs() -> List[Pair]
        Get all pairs in the database.
    update_pair(pair: Pair, new_data: Dict[str, Any]) -> Union[Pair, None]
        Update an existing pair object.
    delete_pair(pair: Pair) -> bool
        Delete a pair object.

    """

    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"


    def create_pair(self, pair: models.Pair) -> Optional[models.Pair]:
        """
        Create a new pair.

        Parameters
        ----------
        pair : Pair
            The pair object to add to the database.

        Returns
        -------
        Optional[Pair]
            The created pair
            or None if not found.
        """
        try:
            self.session.add(pair)
            self.session.commit()
            return pair
        except IntegrityError:
            self.session.rollback()
            return None

    def get_pair(self, **kwargs) -> Optional[models.Pair]:
        """
        Get a pair by its attributes.

        Parameters
        ----------
        **kwargs
            The attributes of the pair to search for.

        Returns
        -------
        Optional[Pair]
            The retrieved pair object, or None if not found.
        """
        return self.session.query(models.Pair).filter_by(**kwargs).first()

    def get_pairs(self) -> List[Type[models.Pair]]:
        """
        Get all pairs in the database.

        Returns
        -------
        List[Pair]
            A list of all pair objects.
        """
        return self.session.query(models.Pair).all()

    def update_pair(self, pair: models.Pair, new_data: Dict[str, Any]) -> Optional[models.Pair]:
        """
        Update an existing pair object.

        Parameters
        ----------
        pair : Pair
            The pair object to update.
        new_data : Dict[str, Any]
            A dictionary containing the attributes to update.

        Returns
        -------
        Optional[Pair]
            The updated pair object, or None if an error occurs.
        """
        try:
            for key, value in new_data.items():
                setattr(pair, key, value)
            self.session.commit()
            return pair
        except IntegrityError:
            self.session.rollback()
            return None

    def delete_pair(self, pair: models.Pair) -> bool:
        """
        Delete a pair object.

        Parameters
        ----------
        pair : Pair
            The pair object to delete.

        Returns
        -------
        bool
            True if the pair is deleted, False if an error occurs.
        """
        try:
            self.session.delete(pair)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            return False



@dataclass
class PoolManager(DatabaseManagerBase):
    """
    PoolManager class for managing CRUD operations on Pool instances.

    Methods
    -------
    create_pool(pool: Pool) -> Union[Pool, None]
        Create a new pool in the database.
    get_pool(**kwargs) -> Optional[Pool]
        Retrieve a single pool from the database based on unique key(s).
    get_pools() -> List[Pool]
        Retrieve all pools from the database.
    update_pool(pool_data: dict, **kwargs) -> Optional[Pool]
        Update a pool in the database based on unique key(s).
    delete_pool(**kwargs) -> bool
        Delete a pool from the database based on unique key(s).
    get_latest_updated_block_by_exchange(exchange_name: str) -> Optional[int]
        Retrieve the latest updated block for a given exchange_name.
    """

    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"


    def create_pool(self, pool: models.Pool) -> Optional[models.Pool]:
        """
        Create a new pool in the database.

        Parameters
        ----------
        pool : Pool
            The Pool instance to be created.

        Returns
        -------
        Union[Pool, None]
            The created Pool instance or None if an error occurred.
        """
        try:
            self.session.add(pool)
            self.session.commit()
            return pool
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating pool: {str(e)}")
            return None

    def get_pool(self, **kwargs) -> Optional[models.Pool]:
        """
        Retrieve a single pool from the database based on unique key(s).

        Parameters
        ----------
        **kwargs
            The unique key(s) for the pool.

        Returns
        -------
        Optional[Pool]
            The found Pool instance or None if not found.
        """
        return self.session.query(models.Pool).filter_by(**kwargs).first()

    def get_pools(self) -> list[Type[Pool]]:
        """
        Retrieve all pools from the database.

        Returns
        -------
        List[Pool]
            A list of all Pool instances in the database.
        """
        return self.session.query(models.Pool).all()

    def update_pool(self, pool_data: dict, **kwargs) -> Optional[models.Pool]:
        """
        Update a pool in the database based on unique key(s).

        Parameters
        ----------
        pool_data : dict
            A dictionary containing the updated attributes.
        **kwargs
            The unique key(s) for the pool.

        Returns
        -------
        Optional[Pool]
            The updated Pool instance or None if an error occurred.
        """
        pool = self.get_pool(**kwargs)
        if pool:
            try:
                pool.update(pool_data)
                self.session.commit()
                return pool
            except IntegrityError as e:
                self.session.rollback()
                print(f"Error updating pool: {str(e)}")
                return None
        return None

    def delete_pool(self, **kwargs) -> bool:
        """
        Delete a pool from the database based on unique key(s).

        Parameters
        ----------
        **kwargs
            The unique key(s) for the pool.

        Returns
        -------
        bool
            True if the pool was deleted, False otherwise.
        """
        pool = self.get_pool(**kwargs)
        if pool:
            try:
                self.session.delete(pool)
                self.session.commit()
                return True
            except IntegrityError as e:
                self.session.rollback()
                print(f"Error deleting pool: {str(e)}")
                return False
        return False

    def get_latest_updated_block_by_exchange(self, exchange_name: str) -> Optional[int]:
        """
        Retrieve the latest updated block for a given exchange_name.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange.

        Returns
        -------
        Optional[int]
            The latest updated block number for the given exchange_name or None if not found.
        """
        pool = (
            self.session.query(Pool)
            .filter(Pool.exchange_name == exchange_name)
            .order_by(Pool.last_updated_block.desc())
            .first()
        )
        return pool.last_updated_block if pool else None

    def get_pool_data_with_tokens(self) -> List[Pool]:
        """
        Retrieve all pools with their token information.

        Returns
        -------
        List[Pool]
            A list of Pool instances with additional token information.
        """
        TokenAlias0 = aliased(models.Token)
        TokenAlias1 = aliased(models.Token)

        # Split pair_name into tkn0 and tkn1 using func.split_part
        tkn0 = func.split_part(Pool.pair_name, '/', 1).label("tkn0")
        tkn1 = func.split_part(Pool.pair_name, '/', 2).label("tkn1")

        return (
            self.session.query(
                Pool,
                tkn0,
                tkn1,
                TokenAlias0.address.label("tkn0_address"),
                TokenAlias0.decimals.label("tkn0_decimals"),
                TokenAlias1.address.label("tkn1_address"),
                TokenAlias1.decimals.label("tkn1_decimals"),
            )
            .outerjoin(TokenAlias0, tkn0 == TokenAlias0.key)
            .outerjoin(TokenAlias1, tkn1 == TokenAlias1.key)
            .all()
        )

