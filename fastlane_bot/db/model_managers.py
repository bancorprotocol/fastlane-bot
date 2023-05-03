"""
Table managers of the Fastlane project..

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from typing import Dict, Any, Type
from typing import List, Optional, Union

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

import fastlane_bot.db.models as models
from fastlane_bot.db.manager_base import DatabaseManagerBase
from fastlane_bot.db.models import Pool, Pair
from fastlane_bot.helpers.poolandtokens import PoolAndTokens


@dataclass
class TokenManager(DatabaseManagerBase):
    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"

    def create_token(self, token: models.Token) -> Optional[models.Token]:
        """
        Create a token in the database

        Parameters
        ----------
        token: models.Token
            The token to create

        Returns
        -------
        Optional[models.Token]
            The created token

        """
        with self.session_scope() as session:
            try:
                session.add(token)
                session.commit()
                self.c.logger.info(f"[model_managers.Token] Successfully created token: {token.key}")
                session.expunge_all()
                return token
            except Exception as e:
                self.c.logger.error(f"[model_managers.Token] Failed to create token: {e}")
                raise


    def get_token(self, **kwargs) -> Optional[models.Token]:
        """
        Get a token from the database

        Parameters
        ----------
        **kwargs
            The token's attributes to filter by

        Returns
        -------
        Optional[models.Token]
            The token if found, None otherwise

        """
        with self.session_scope() as session:
            token = session.query(models.Token).filter_by(**kwargs).first()
            session.expunge_all()
            return token

    def get_tokens(self) -> List[Type[models.Token]]:
        """
        Get all tokens from the database

        Returns
        -------
        List[Type[models.Token]]
            A list of all tokens in the database
        """
        with self.session_scope() as session:
            tokens = session.query(models.Token).all()
            session.expunge_all()
            return list(tokens)

    def update_token(self, token: models.Token, new_data: Dict[str, Any]) -> Optional[models.Token]:
        """
        Update a token in the database

        Parameters
        ----------
        token: models.Token
            The token to update
        new_data: Dict[str, Any]
            The new data to update the token with

        Returns
        -------
        Optional[models.Token]
            The updated token

        """
        updated = False  # Flag to track if any value has been updated

        with self.session_scope() as session:
            try:
                for key, value in new_data.items():
                    if getattr(token, key) != value:  # Check if the current value is different from the new value
                        setattr(token, key, value)
                        updated = True

                if updated:  # Only commit and log the message if any value has been updated
                    session.commit()
                    session.expunge_all()
                    self.c.logger.info(f"[model_managers.Token] Successfully updated token: {token.key}")
                else:
                    self.c.logger.info(f"[model_managers.Token] No changes detected for token: {token.key}")

                return token
            except Exception as e:
                self.c.logger.error(f"[model_managers.Token] Failed to update token: {token.key}")
                raise  # Allow the exception to propagate to the session_scope context manager

    def delete_token(self, token: models.Token) -> bool:
        """
        Delete a token from the database

        Parameters
        ----------
        token: models.Token
            The token to delete

        Returns
        -------
        bool
            True if the token was deleted successfully, False otherwise

        """
        with self.session_scope() as session:
            try:
                session.delete(token)
                session.commit()
                self.c.logger.info(f"[model_managers.Token] Successfully deleted token: {token.key}")
                session.expunge_all()
                return True
            except Exception as e:
                self.c.logger.error(f"[model_managers.Token] Failed to delete token: {token.key}")
                raise  # Allow the exception to propagate to the session_scope context manager


@dataclass
class PairManager(DatabaseManagerBase):
    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"

    def create_pair(self, pair: models.Pair or Dict[str, Any]) -> Optional[models.Pair]:
        """
        Create a pair in the database

        Parameters
        ----------
        pair: models.Pair or Dict[str, Any]
            The pair to create


        Returns
        -------
        Optional[models.Pair]
            The created pair

        """
        if isinstance(pair, dict):
            pair = models.Pair(**pair)

        with self.session_scope() as session:
            try:
                session.add(pair)
                session.commit()
                self.c.logger.info(f"[model_managers.Pair] Successfully created pair: {pair.id}")
                session.expunge_all()
                return pair
            except Exception as e:
                self.c.logger.error(f"[model_managers.Pair] Failed to create pair: {e}")
                raise # Allow the exception to propagate to the session_scope context manager

    def get_pair(self, **kwargs) -> Optional[models.Pair]:
        """
        Get a pair from the database
        """
        with self.session_scope() as session:
            pair = session.query(models.Pair).filter_by(**kwargs).first()
            session.expunge_all()
            return pair

    def get_pairs(self) -> List[Type[models.Pair]]:
        """
        Get all pairs from the database
        """
        with self.session_scope() as session:
            pairs = session.query(models.Pair).all()
            session.expunge_all()
            return list(pairs)

    def update_pair(self, pair: models.Pair, new_data: Dict[str, Any]) -> Optional[models.Pair]:
        """
        Update a pair in the database

        Parameters
        ----------
        pair: models.Pair
            The pair to update
        new_data: Dict[str, Any]
            The new data to update the pair with

        Returns
        -------
        Optional[models.Pair]
            The updated pair

        """
        updated = False  # Flag to track if any value has been updated

        with self.session_scope() as session:
            try:
                for key, value in new_data.items():
                    if getattr(pair, key) != value:  # Check if the current value is different from the new value
                        setattr(pair, key, value)
                        updated = True

                if updated:  # Only commit and log the message if any value has been updated
                    session.commit()
                    session.expunge_all()
                    self.c.logger.info(f"[model_managers.Pair] Successfully updated pair: {pair.name}")
                else:
                    self.c.logger.info(f"[model_managers.Pair] No changes detected for pair: {pair.name}")

                return pair
            except Exception as e:
                self.c.logger.error(f"[model_managers.Pair] Failed to update pair: {pair.name}")
                raise  # Allow the exception to propagate to the session_scope context manager

    def delete_pair(self, pair: models.Pair) -> bool:
        """
        Delete a pair from the database

        Parameters
        ----------
        pair: models.Pair
            The pair to delete

        Returns
        -------
        bool
            True if the pair was deleted successfully, False otherwise

        """

        with self.session_scope() as session:
            try:
                session.delete(pair)
                session.commit()
                self.c.logger.info(f"[model_managers.Pair] Successfully deleted pair: {pair.name}")
                session.expunge_all()
                return True
            except Exception as e:
                self.c.logger.error(f"[model_managers.Pair] Failed to delete pair: {pair.name}")
                raise  # Allow the exception to propagate to the session_scope context manager


@dataclass
class PoolManager(DatabaseManagerBase):
    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"

    def create_pool(self, pool: models.Pool or Dict[str, Any]) -> Optional[models.Pool]:
        """
        Create a new pool in the database

        Parameters
        ----------
        pool: models.Pool or Dict[str, Any]
            The pool to create

        Returns
        -------
        Optional[models.Pool]
            The created pool

        """
        if isinstance(pool, dict):
            pool = models.Pool(**pool)

        with self.session_scope() as session:
            try:
                session.add(pool)
                session.commit()
                self.c.logger.info(f"[model_managers.Pool] Created pool on {pool.exchange_name}: {pool.pair_name}")
                session.expunge_all()
                return pool
            except Exception as e:
                self.c.logger.error(f"[model_managers.Pool] Error creating pool on {pool.exchange_name}: {str(e)}")
                raise  # Allow the exception to propagate to the session_scope context manager

    def get_pool(self, **kwargs) -> Optional[models.Pool]:
        with self.session_scope() as session:
            pool = session.query(models.Pool).filter_by(**kwargs).first()
            session.expunge_all()
            return pool

    def get_pools(self) -> List[Type[Pool]]:
        """
        Retrieve all pools from the database.
        """
        with self.session_scope() as session:
            pools = session.query(models.Pool).all()
            session.expunge_all()
            return list(pools)

    def update_pool(self, pool_data: Dict[str, Any], **kwargs) -> Optional[models.Pool]:
        """
        Update a pool in the database.

        Parameters
        ----------
        pool_data
            The data to update the pool with.
        kwargs
            The pool to update.

        Returns
        -------
        Optional[models.Pool]
            The updated pool.

        """
        updated = False  # Flag to track if any value has been updated

        pool = self.get_pool(**kwargs)
        if not pool:
            self.c.logger.error(f"[model_managers.Pool] Failed to update pool, pool not found: {kwargs}")
            return None

        with self.session_scope() as session:
            try:
                for key, value in pool_data.items():
                    if getattr(pool, key) != value:  # Check if the current value is different from the new value
                        setattr(pool, key, value)
                        updated = True

                if updated:  # Only commit and log the message if any value has been updated
                    session.commit()
                    session.expunge_all()
                    self.c.logger.info(f"[model_managers.Pool] Successfully updated pool: {pool.pair_name}")
                else:
                    self.c.logger.info(f"[model_managers.Pool] No changes detected for pool: {pool.pair_name}")

                return pool
            except Exception as e:
                self.c.logger.error(f"[model_managers.Pool] Failed to update pair: {pool.pair_name}")
                raise  # Allow the exception to propagate to the session_scope context manager

    def delete_pool(self, **kwargs) -> bool:
        """
        Delete a pool from the database.

        Parameters
        ----------
        kwargs

        Returns
        -------
        bool
            True if the pool was deleted, False otherwise.

        """

        pool = self.get_pool(**kwargs)

        with self.session_scope() as session:
            if pool:
                try:
                    session.delete(pool)
                    session.commit()
                    self.c.logger.info(f"[model_managers.Pool] Successfully deleted pool: {pool.id}")
                    session.expunge_all()
                    return True
                except IntegrityError as e:
                    self.c.logger.error(f"[model_managers.Pool] Error deleting pool: {str(e)}")
                    raise  # Allow the exception to propagate to the session_scope context manager
            return False

    def get_latest_updated_block_by_exchange(self, exchange_name: str) -> Optional[int]:
        """
        Get the latest updated block for a given exchange.

        Parameters
        ----------
        exchange_name
            The name of the exchange to get the latest updated block for.

        Returns
        -------
        Optional[int]
            The latest updated block for the given exchange.

        """
        with self.session_scope() as session:
            pool = (
                session.query(Pool)
                .filter(Pool.exchange_name == exchange_name)
                .order_by(Pool.last_updated_block.desc())
                .first()
            )
            session.expunge_all()
            return pool.last_updated_block if pool else None

    def get_pool_data_with_tokens(self, cnfg: Any) -> List[PoolAndTokens]:
        """
        Get pool data with tokens.

        Parameters
        ----------
        cnfg
            The configuration to use.

        Returns
        -------
        List[PoolAndTokens]
            The pool data with token data.

        """

        with self.session_scope() as session:
            TokenAlias0 = aliased(models.Token)
            TokenAlias1 = aliased(models.Token)

            # Split pair_name into tkn0 and tkn1 using func.split_part
            tkn0 = func.split_part(Pool.pair_name, '/', 1).label("tkn0")
            tkn1 = func.split_part(Pool.pair_name, '/', 2).label("tkn1")

            pool_and_tokens = (session.query(
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
                               .all())
            session.expunge_all()
            return [
                PoolAndTokens(
                    ConfigObj=cnfg,
                    id=row[0].id,
                    cid=row[0].cid,
                    last_updated=row[0].last_updated,
                    last_updated_block=row[0].last_updated_block,
                    descr=row[0].descr,
                    pair_name=row[0].pair_name,
                    exchange_name=row[0].exchange_name,
                    fee=row[0].fee,
                    tkn0_balance=row[0].tkn0_balance,
                    tkn1_balance=row[0].tkn1_balance,
                    z_0=row[0].z_0,
                    y_0=row[0].y_0,
                    A_0=row[0].A_0,
                    B_0=row[0].B_0,
                    z_1=row[0].z_1,
                    y_1=row[0].y_1,
                    A_1=row[0].A_1,
                    B_1=row[0].B_1,
                    sqrt_price_q96=row[0].sqrt_price_q96,
                    tick=row[0].tick,
                    tick_spacing=row[0].tick_spacing,
                    liquidity=row[0].liquidity,
                    address=row[0].address,
                    anchor=row[0].anchor,
                    tkn0=row[1],
                    tkn1=row[2],
                    tkn0_address=row[3],
                    tkn0_decimals=row[4],
                    tkn1_address=row[5],
                    tkn1_decimals=row[6],
                )
                for row in pool_and_tokens
            ]
