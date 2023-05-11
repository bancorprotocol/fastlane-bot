"""
Table managers of the Fastlane project..

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, Type
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

import fastlane_bot.db.models as models
from fastlane_bot.db.manager_base import DatabaseManagerBase, session
from fastlane_bot.db.models import Pool
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
        try:
            session.add(token)
            session.commit()
            return token

        except Exception as e:
            print(f"[model_managers.Token] Failed to create token: {e}")
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
        token = session.query(models.Token).filter_by(**kwargs).first()

        return token

    def get_tokens(self) -> List[Type[models.Token]]:
        """
        Get all tokens from the database

        Returns
        -------
        List[Type[models.Token]]
            A list of all tokens in the database
        """
        tokens = session.query(models.Token).all()

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

        try:
            for key, value in new_data.items():
                if getattr(token, key) != value:  # Check if the current value is different from the new value
                    setattr(token, key, value)
                    updated = True

            if updated:  # Only commit and log the message if any value has been updated
                session.commit()

            else:
                print(f"[model_managers.Token] No changes detected for token: {token.key}")

            return token
        except Exception as e:
            print(f"[model_managers.Token] Failed to update token: {token.key}")
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
        try:
            session.delete(token)
            session.commit()
            return True

        except Exception as e:
            print(f"[model_managers.Token] Failed to delete token: {token.key}")
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

        try:
            session.add(pair)
            session.commit()
            return pair

        except Exception as e:
            print(f"[model_managers.Pair] Failed to create pair: {e}")
            raise  # Allow the exception to propagate to the session_scope context manager

    def get_pair(self, **kwargs) -> Optional[models.Pair]:
        """
        Get a pair from the database
        """
        return session.query(models.Pair).filter_by(**kwargs).first()

    def get_pairs(self) -> List[Type[models.Pair]]:
        """
        Get all pairs from the database
        """
        return session.query(models.Pair).all()

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

        try:
            for key, value in new_data.items():
                if getattr(pair, key) != value:  # Check if the current value is different from the new value
                    setattr(pair, key, value)
                    updated = True

            if updated:  # Only commit and log the message if any value has been updated
                session.commit()

            else:
                print(f"[model_managers.Pair] No changes detected for pair: {pair.name}")

            return pair
        except Exception as e:
            print(f"[model_managers.Pair] Failed to update pair: {pair.name}")
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

        try:
            session.delete(pair)
            session.commit()
            return True

        except Exception as e:
            print(f"[model_managers.Pair] Failed to delete pair: {pair.name}")
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

        try:
            session.add(pool)
            session.commit()
            return pool

        except Exception as e:
            print(f"[model_managers.Pool] Error creating pool on {pool.exchange_name}: {str(e)}")
            raise  # Allow the exception to propagate to the session_scope context manager

    def get_pool(self, **kwargs) -> Optional[models.Pool]:
        return session.query(models.Pool).filter_by(**kwargs).first()

    def get_pools(self) -> List[Type[Pool]]:
        """
        Retrieve all pools from the database.
        """
        return session.query(models.Pool).all()

    def update_pool(self, pool_data: Dict[str, Any], all_data: Dict[str, Any], **kwargs) -> Optional[models.Pool]:
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
        pool = self.get_pool(cid=pool_data['cid'])
        if not pool:
            print(f"[model_managers.Pool] Failed to update pool, pool not found: {kwargs}")
            return None

        try:
            # remove "id" from pool_data
            pool_data.pop('id', None)
            pool = self.create_or_update_pool(pool_data)
            return pool
        except Exception as e:
            session.rollback()
            try:
                pair = self.get_pair(name=pool_data['pair_name'])
                if not pair:
                    pair_data = {
                        'name': all_data['pair_name'],
                        'tkn0_address': all_data['tkn0_address'],
                        'tkn1_address': all_data['tkn1_address'],
                        'tkn0_key': all_data['tkn0_key'],
                        'tkn1_key': all_data['tkn1_key'],
                    }
                    self.create_pair(pair_data)
                    self.create_or_update_pool(pool, pool_data)
            except Exception as e:
                print(f"[model_managers.Pool] Failed to update pair: {str(e)} - {pool}  skipping...")

    def create_or_update_pool(self, pool_data: Dict[str, Any]) -> models.Pool:
        """
        Create or update a pool in the database.

        Parameters
        ----------
        pool : models.Pool
            The pool to update.

        pool_data : Dict[str, Any]
            The data to update the pool with.

        Returns
        -------
        models.Pool
            The updated pool.

        """
        existing_pool = session.query(models.Pool).filter(models.Pool.cid == pool_data['cid']).first()
        if existing_pool:
            for key, value in pool_data.items():
                setattr(existing_pool, key, value)
            pool = existing_pool
        else:
            pool = models.Pool(**pool_data)
            session.add(pool)
        session.commit()
        return pool

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

        if pool:
            try:
                session.delete(pool)
                session.commit()

                return True
            except IntegrityError as e:
                print(f"[model_managers.Pool] Error deleting pool: {str(e)}")
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
        pool = (
            session.query(Pool)
            .filter(Pool.exchange_name == exchange_name)
            .order_by(Pool.last_updated_block.desc())
            .first()
        )

        return pool.last_updated_block if pool else None

    def get_pool_data_with_tokens(self) -> List[PoolAndTokens]:
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

        return [
            PoolAndTokens(
                ConfigObj=self.ConfigObj,
                id=row[0].id,
                cid=row[0].cid,
                last_updated=row[0].last_updated,
                last_updated_block=row[0].last_updated_block,
                descr=row[0].descr,
                pair_name=row[0].pair_name,
                exchange_name=row[0].exchange_name,
                fee=row[0].fee_float,
                fee_float=row[0].fee_float,
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

    def create_pool_pair_tokens(self, pool_pair_tokens: models.Pool or Dict[str, Any]):
        if not isinstance(pool_pair_tokens, dict):
            return
        pool_pair_tokens["cid"] = str(pool_pair_tokens["cid"])
        exchange_name = pool_pair_tokens["exchange_name"]

        exchange = session.query(models.Exchange).filter(models.Exchange.name == exchange_name).first()

        if not exchange:
            exchange = models.Exchange(name=exchange_name)
            session.add(exchange)
            session.commit()

        token0_params = {
            "address": pool_pair_tokens["tkn0_address"],
            "decimals": pool_pair_tokens["tkn0_decimals"],
            "symbol": pool_pair_tokens["tkn0_symbol"],
            "key": pool_pair_tokens["tkn0_key"],
            "name": pool_pair_tokens["tkn0_symbol"],
        }
        token0 = self.get_token(key=token0_params["key"])
        if not token0:
            self._extracted_from_create_pool_pair_tokens(token0_params)
        token1_params = {
            "address": pool_pair_tokens["tkn1_address"],
            "decimals": pool_pair_tokens["tkn1_decimals"],
            "symbol": pool_pair_tokens["tkn1_symbol"],
            "key": pool_pair_tokens["tkn1_key"],
            "name": pool_pair_tokens["tkn1_symbol"],
        }
        token1 = self.get_token(key=token1_params["key"])
        if not token1:
            self._extracted_from_create_pool_pair_tokens(token1_params)
        pair_params = {
            "name": pool_pair_tokens["pair_name"],
            "tkn0_address": pool_pair_tokens["tkn0_address"],
            "tkn1_address": pool_pair_tokens["tkn1_address"],
            "tkn0_key": pool_pair_tokens["tkn0_key"],
            "tkn1_key": pool_pair_tokens["tkn1_key"],
        }
        pair = self.get_pair(**pair_params)
        if not pair:
            pair = models.Pair(**pair_params)
            try:
                session.add(pair)
                session.commit()
            except Exception as e:
                print(f"Error creating pair: {e}, skipping")
                session.rollback()

    def _extracted_from_create_pool_pair_tokens(self, arg0: Dict[str, Any]) -> None:

        token0 = models.Token(**arg0)
        session.add(token0)
        session.commit()
