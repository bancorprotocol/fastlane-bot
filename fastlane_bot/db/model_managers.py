"""
Table managers of the Fastlane project..

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
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
    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"

    def create_token(self, token: models.Token) -> Optional[models.Token]:

        try:
            self.session.add(token)
            self.session.commit()
            return token
        except IntegrityError:
            self.session.rollback()
            return None

    def get_token(self, **kwargs) -> Optional[models.Token]:

        return self.session.query(models.Token).filter_by(**kwargs).first()

    def get_tokens(self) -> List[Type[models.Token]]:

        return self.session.query(models.Token).all()

    def update_token(self, token: models.Token, new_data: Dict[str, Any]) -> Optional[models.Token]:

        try:
            for key, value in new_data.items():
                setattr(token, key, value)
            self.session.commit()
            return token
        except IntegrityError:
            self.session.rollback()
            return None

    def delete_token(self, token: models.Token) -> bool:

        try:
            self.session.delete(token)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            return False


@dataclass
class PairManager(DatabaseManagerBase):
    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"

    def create_pair(self, pair: models.Pair) -> Optional[models.Pair]:

        try:
            self.session.add(pair)
            self.session.commit()
            return pair
        except IntegrityError:
            self.session.rollback()
            return None

    def get_pair(self, **kwargs) -> Optional[models.Pair]:

        return self.session.query(models.Pair).filter_by(**kwargs).first()

    def get_pairs(self) -> List[Type[models.Pair]]:

        return self.session.query(models.Pair).all()

    def update_pair(self, pair: models.Pair, new_data: Dict[str, Any]) -> Optional[models.Pair]:

        try:
            for key, value in new_data.items():
                setattr(pair, key, value)
            self.session.commit()
            return pair
        except IntegrityError:
            self.session.rollback()
            return None

    def delete_pair(self, pair: models.Pair) -> bool:

        try:
            self.session.delete(pair)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            return False


@dataclass
class PoolManager(DatabaseManagerBase):
    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"

    def create_pool(self, pool: models.Pool) -> Optional[models.Pool]:

        try:
            self.session.add(pool)
            self.session.commit()
            return pool
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating pool: {str(e)}")
            return None

    def get_pool(self, **kwargs) -> Optional[models.Pool]:

        return self.session.query(models.Pool).filter_by(**kwargs).first()

    def get_pools(self) -> List[Type[Pool]]:
        """
        Retrieve all pools from the database.
        """
        return self.session.query(models.Pool).all()

    def update_pool(self, pool_data: dict, **kwargs) -> Optional[models.Pool]:
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
            self.session.query(Pool)
            .filter(Pool.exchange_name == exchange_name)
            .order_by(Pool.last_updated_block.desc())
            .first()
        )
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

        TokenAlias0 = aliased(models.Token)
        TokenAlias1 = aliased(models.Token)

        # Split pair_name into tkn0 and tkn1 using func.split_part
        tkn0 = func.split_part(Pool.pair_name, '/', 1).label("tkn0")
        tkn1 = func.split_part(Pool.pair_name, '/', 2).label("tkn1")

        pool_and_tokens = (self.session.query(
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
