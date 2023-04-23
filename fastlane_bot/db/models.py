"""
Backend models for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union, Any, Dict, List

from _decimal import Decimal
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

from fastlane_bot.config import *
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.utils import (
    EncodedOrder,
    UniV3Helper,
)

from sqlalchemy.orm import registry

global contracts
contracts = {}

mapper_registry = registry()
logged_keys = []


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
        self.id = EXCHANGE_IDS[self.name]


@mapper_registry.mapped
@dataclass
class Token:
    """
    Represents a tkn_address on a blockchain.

    symbol: The symbol of the tkn_address. (unique) (non-null)
    name: The name of the tkn_address. (nullable)
    address: The address of the tkn_address. (unique) (non-null)
    :params decimals: The number of decimals the tkn_address has. (default: 18) (non-null)
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
    key: str = field(init=False)

    def is_eth(self) -> bool:
        """
        True if the tkn_address is ETH
        """
        return self.symbol == "ETH"

    def is_weth(self) -> bool:
        """
        True if the tkn_address is WETH
        """
        return self.symbol == "WETH"


@mapper_registry.mapped
@dataclass
class Pair:
    """
    Represents a pair of tokens on a blockchain.

    name: The name of the pair. (unique) (non-null)
    """

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

    def to_eth(self):
        """
        True if the pair is ETH/TKN
        """
        self.name = self.name.replace("WETH", "ETH")

    def to_weth(self):
        """
        True if the pair is WETH/TKN
        """
        self.name = self.name.replace("ETH", "WETH")


@mapper_registry.mapped
@dataclass
class Pool:
    """
    Represents a liquidity pool on an exchange. The combination of the pair name and exchange name must be unique.
    NOTE: foreign key relations must pre-exist in the database.

    System Generated (required):
    id: The auto-incrementing id of the pool. (primary key) (non-null) (unique) (auto-increment)
    last_updated (datetime): The last time the pool was updated. (default: now) (auto-update)

    User Provided (required):
    pair_name (str): The name of the pair of tokens in the pool. (foreign key to Pair)
    exchange_name (str): The name of the exchange the pool is on. (foreign key to Exchange)

    User Provided (optional):
    cid (int): The id of the pool provided by the exchange / contract. (unique) (default: id)
    descr (str): A description of the pool.
    tkn0_symbol (str): The symbol of tkn_address 0 in the pool. (foreign key to Token)
    tkn1_symbol (str): The symbol of tkn_address 1 in the pool. (foreign key to Token)
    fee (str): The fee of the pool. (default: "0")
    tkn0_balance (int): The balance of tkn_address 0 in the pool. (default: 0)
    tkn1_balance (int): The balance of tkn_address 1 in the pool. (default: 0)
    sqrt_price_q96 (int): The UniV3 sqrt price of the pool. (default: 0)
    liquidity (int): The UniV3 liquidity of the pool. (default: 0)
    tick (int): The UniV3 tick of the pool. (default: 0)
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
        Column("descr", String(100), nullable=True),
        Column("pair_name", String(100), ForeignKey("pairs.name")),
        Column("exchange_name", String(100), ForeignKey("exchanges.name")),
        Column("fee", String(20), nullable=False, default="0"),
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

    id: int
    cid: str
    last_updated: Optional[datetime] = None
    last_updated_block: Optional[int] = None
    contract_initialized: Optional[bool] = False
    fee: Optional[str] = None
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

    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                setattr(self, key, value)


@mapper_registry.mapped
@dataclass
class Transaction:
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



