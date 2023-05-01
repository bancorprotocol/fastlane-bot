"""
Backend models for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    PrimaryKeyConstraint,
    DateTime,
    BigInteger,
    Numeric,
    UniqueConstraint,
    Float,
    Boolean,
)

global contracts
contracts = {}
from decimal import Decimal
from sqlalchemy.orm import registry

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class Blockchain:
    """
    Represents a blockchain.

    name: The name of the blockchain. (default: Ethereum) (unique)
    """

    __table__ = Table(
        "blockchains",
        mapper_registry.metadata,
        Column(
            "id", Integer, primary_key=True, autoincrement=True, index=True, unique=True
        ),
        Column(
            "name",
            String(50),
            index=True,
            unique=True,
            nullable=False,
            default="Ethereum",
        ),
        Column("block_number", Integer, nullable=False, default=0),
    )

    id: int = field(init=False)
    name: Optional[str] = None
    block_number: Optional[int] = None


@mapper_registry.mapped
@dataclass
class Exchange:
    """
    Represents an exchange on a blockchain.

    name: The name of the exchange. (unique) (non-null)
    blockchain_name: The name of the blockchain the exchange is on. (non-null)
    """

    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"

    # TODO: attach exchange ids to the config somehow

    EXCHANGE_IDS = {
        "bancor_v2": 1,
        "bancor_v3": 2,
        "uniswap_v2": 3,
        "uniswap_v3": 4,
        "sushiswap_v2": 5,
        "carbon_v1": 6,
    }

    __table__ = Table(
        "exchanges",
        mapper_registry.metadata,
        Column("id", Integer, primary_key=True, index=True, unique=True),
        Column("name", String(50), unique=True, nullable=False),
        Column(
            "blockchain_name",
            String(50),
            ForeignKey("blockchains.name"),
            nullable=False,
        ),
    )

    id: int = field(init=False)
    name: Optional[str] = None
    blockchain_name: Optional[str] = None

    def __post_init__(self):
        self.id = self.EXCHANGE_IDS[self.name] if 'test' not in self.name.lower() else 10000


@mapper_registry.mapped
@dataclass
class Token:
    """
    Represents a tkn_address on a blockchain.

    Parameters
    ----------
    symbol : str
        The symbol of the token
    name : str
        The name of the token
    address : str
        The address of the token
    decimals : int
        The number of decimals of the token
    key : str
        The key of the token

    """

    __table__ = Table(
        "tokens",
        mapper_registry.metadata,
        Column(
            "id", Integer, primary_key=True, index=True, unique=True, autoincrement=True
        ),
        Column("key", String(100), nullable=True, index=True, unique=True),
        Column("symbol", String(100), nullable=False, index=True, unique=False),
        Column("name", String(100), nullable=True, index=True, unique=False),
        Column("address", String(64), index=True, unique=True, nullable=False),
        Column("decimals", Integer, nullable=False, default=18),
    )

    id: int = field(init=False)
    symbol: str
    name: str
    address: str
    decimals: int
    key: str



@mapper_registry.mapped
@dataclass
class Pair:
    """
    Represents a pair of tokens on a blockchain.

    Parameters
    ----------
    name : str
        The name of the pair
    tkn0_address : str
        The address of the first token
    tkn1_address : str
        The address of the second token
    tkn0_key : str
        The key of the first token
    tkn1_key : str
        The key of the second token

    """

    __VERSION__ = "3.0.2"
    __DATE__ = "05-01-2023"

    __table__ = Table(
        "pairs",
        mapper_registry.metadata,
        Column("id", Integer, primary_key=True, index=True, unique=True),
        Column("name", String(100), index=True, unique=True, nullable=False),
        Column(
            "tkn0_address",
            String(64),
            ForeignKey("tokens.address"),
            nullable=False,
            index=True,
        ),
        Column(
            "tkn1_address",
            String(64),
            ForeignKey("tokens.address"),
            nullable=False,
            index=True,
        ),
        Column(
            "tkn0_key",
            String(100),
            ForeignKey("tokens.key"),
            nullable=False,
            index=True,
        ),
        Column(
            "tkn1_key",
            String(100),
            ForeignKey("tokens.key"),
            nullable=False,
            index=True,
        ),
    )
    __unique_constraints__ = (
        UniqueConstraint("tkn0_address", "tkn1_address"),
        UniqueConstraint("tkn0_key", "tkn1_key"),
    )

    id: int = field(init=False)
    name: Optional[str] = None
    tkn0_address: Optional[str] = None
    tkn1_address: Optional[str] = None
    tkn0_key: Optional[str] = None
    tkn1_key: Optional[str] = None



@mapper_registry.mapped
@dataclass
class Pool:
    """
    Represents a liquidity pool on an exchange.

    Parameters
    ----------
    cid : str
        The cid of the pool
    last_updated : datetime
        The last time the pool was updated
    last_updated_block : int
        The last block the pool was updated
    descr : str
        The description of the pool
    pair_name : str
        The name of the pair
    exchange_name : str
        The name of the exchange
    fee : float
        The fee of the pool
    tkn0_balance : float
        The balance of the first token
    tkn1_balance : float
        The balance of the second token
    z_0 : float
        The z_0 of the pool
    z_1 : float
        The z_1 of the pool
    y_0 : float
        The y_0 of the pool
    y_1 : float
        The y_1 of the pool
    A_0 : float
        The A_0 of the pool
    A_1 : float
        The A_1 of the pool
    B_0 : float
        The B_0 of the pool
    B_1 : float
        The B_1 of the pool
    sqrt_price_q96: float
        The sqrt_price_q96 of the pool
    tick: int
        The tick of the pool
    liquidity: float
        The liquidity of the pool
    tick_spacing: int
        The tick_spacing of the pool
    address: str
        The address of the pool
    anchor: str
        The anchor of the pool

    """

    __table__ = Table(
        "pools",
        mapper_registry.metadata,
        Column(
            "id",
            BigInteger,
            primary_key=True,
            index=True,
            unique=True,
            autoincrement=True,
        ),
        Column("cid", String(128), nullable=False, unique=True, index=True),
        Column(
            "last_updated",
            DateTime,
            nullable=False,
            default=datetime.utcnow,
            index=True,
            unique=False,
            onupdate=datetime.utcnow,
        ),
        Column(
            "last_updated_block",
            BigInteger,
            nullable=False,
            index=True,
            unique=False,
        ),
        Column("descr", String(500), nullable=True),
        Column("pair_name", String(500), ForeignKey("pairs.name")),
        Column("exchange_name", String(100), ForeignKey("exchanges.name")),
        Column("fee", String(20), nullable=False, default="0"),
        Column("fee_float", Numeric(precision=10), nullable=False, default=0),
        Column("tkn0_balance", Numeric(precision=64), nullable=True),
        Column("tkn1_balance", Numeric(precision=64), nullable=True),
        Column("z_0", Numeric(precision=64), nullable=True),
        Column("y_0", Numeric(precision=64), nullable=True),
        Column("A_0", Numeric(precision=64), nullable=True),
        Column("B_0", Numeric(precision=64), nullable=True),
        Column("z_1", Numeric(precision=64), nullable=True),
        Column("y_1", Numeric(precision=64), nullable=True),
        Column("A_1", Numeric(precision=64), nullable=True),
        Column("B_1", Numeric(precision=64), nullable=True),
        Column(
            "sqrt_price_q96", Numeric(precision=64), nullable=True, default=Decimal("0")
        ),
        Column("tick", BigInteger, nullable=True),
        Column("tick_spacing", BigInteger, nullable=True),
        Column("liquidity", Numeric(precision=64), nullable=True),
        Column(
            "address",
            String(64),
            index=True,
            unique=False,
            nullable=True,
        ),
        Column(
            "anchor",
            String(64),
            index=True,
            unique=False,
            nullable=True,
        ),
    )
    __unique_constraints__ = (
        PrimaryKeyConstraint("pair_name", "fee", "exchange_name", name="pair_key"),
    )

    id: int = field(init=False)
    cid: str
    last_updated: Optional[datetime] = None
    last_updated_block: Optional[int] = None
    contract_initialized: Optional[bool] = False
    fee: Optional[str] = None
    fee_float: Optional[float] = None
    address: Optional[str] = None
    anchor: Optional[str] = None
    pair_name: Optional[str] = None
    tkn0_address: Optional[str] = None
    tkn1_address: Optional[str] = None
    tkn0_key: Optional[str] = None
    tkn1_key: Optional[str] = None
    exchange_name: Optional[str] = None
    tkn0_balance: Optional[Decimal] = None
    tkn1_balance: Optional[Decimal] = None
    sqrt_price_q96: Optional[Decimal] = None
    tick: Optional[int] = None
    tick_spacing: Optional[int] = None
    liquidity: Optional[Decimal] = None
    z_0: Optional[Decimal] = None
    y_0: Optional[Decimal] = None
    A_0: Optional[Decimal] = None
    B_0: Optional[Decimal] = None
    z_1: Optional[Decimal] = None
    y_1: Optional[Decimal] = None
    A_1: Optional[Decimal] = None
    B_1: Optional[Decimal] = None

    def __post_init__(self):
        self.descr = (
            self.descr
            if self.descr is not None
            else f"{self.exchange_name} {self.pair_name} {self.fee}"
        )

        if self.exchange_name == 'uniswap_v3':  # TODO: name should be in config (how???)
            self.fee_float = float(self.fee) / 1000000
        else:
            self.fee_float = float(self.fee) if self.fee is not None else 0.0

    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                setattr(self, key, value)


@mapper_registry.mapped
@dataclass
class Transaction:
    """
    A class used to represent a transaction

    Parameters
    ----------
    id : int
        The id of the transaction
    last_updated : datetime
        The last_updated of the transaction
    trade_route_id : str
        The trade_route_id of the transaction
    token_in : str
        The token_in of the transaction
    amount_in : float
        The amount_in of the transaction
    token_out : str
        The token_out of the transaction
    amount_out : float
        The amount_out of the transaction
    succeeded : bool
        The succeeded of the transaction
    gas_price : int
        The gas_price of the transaction
    max_priority_fee : int
        The max_priority_fee of the transaction
    transaction_hash : str
        The transaction_hash of the transaction
    failure_reason : str
        The failure_reason of the transaction

    """
    __table__ = Table(
        "transactions",
        mapper_registry.metadata,
        Column(
            "id", Integer, primary_key=True, autoincrement=True, index=True, unique=True
        ),
        Column(
            "last_updated",
            DateTime,
            nullable=False,
            default=datetime.utcnow,
            index=True,
            unique=True,
            onupdate=datetime.utcnow,
        ),
        Column("trade_route_id", String(50), nullable=False),
        Column("token_in", String(50), nullable=False),
        Column("amount_in", Float, nullable=False),
        Column("token_out", String(50), nullable=False),
        Column("amount_out", Float, nullable=False),
        Column("succeeded", Boolean, nullable=False),
        Column("gas_price", Integer, nullable=True),
        Column("max_priority_fee", Integer, nullable=True),
        Column("transaction_hash", String(66), nullable=True),
        Column("failure_reason", String(255), nullable=True),
    )

    id: int = field(init=False)
    last_updated: Optional[datetime] = field(init=False)
    trade_route_id: str
    token_in: str
    amount_in: float
    token_out: str
    amount_out: float
    succeeded: bool
    gas_price: int = field(default=None)
    max_priority_fee: int = field(default=None)
    transaction_hash: str = field(default=None)
    failure_reason: str = field(default=None)



