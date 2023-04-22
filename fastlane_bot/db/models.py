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
    get_abi_and_router,
    convert_decimals,
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

    @staticmethod
    def convert_decimals(tkn_balance: Decimal, tkn_decimals: int) -> Decimal:
        """
        Correct the decimals of the tokens in the pool.
        """
        return Decimal(str(tkn_balance / (Decimal("10") ** Decimal(str(tkn_decimals)))))

    @staticmethod
    def _validate_arg_types(typed_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        convert the arguments to the correct type if numeric values, else leave as is
        :param typed_args: dictionary of arguments with types
        :return:         dictionary of arguments with types converted to the correct type
        """
        arg_type = float
        for key, value in typed_args.items():
            if isinstance(value, (Decimal, float, int)):
                typed_args[key] = arg_type(value)
        return typed_args

    def to_cpc(
        self, numerical_type: str = "float", db: Any = None
    ) -> Union[ConstantProductCurve, List[Any]]:
        """
        Returns an instance of the ConstantProductCurve class.

        :param numerical_type: The type of numerical values. Options are "decimal" or "float".
        """
        tkn0_key = self.pair_name.split("/")[0]
        tkn1_key = self.pair_name.split("/")[1]
        tkn0 = db.session.query(Token).filter(Token.key == tkn0_key).first()
        tkn1 = db.session.query(Token).filter(Token.key == tkn1_key).first()

        cpc = ConstantProductCurve
        self.fee = float(Decimal(self.fee))
        if self.exchange_name == UNISWAP_V3_NAME:
            out = self._univ3_to_cpc(cpc, tkn0, tkn1)
        elif self.exchange_name == CARBON_V1_NAME:
            out = self._carbon_to_cpc(cpc, tkn0, tkn1)
        elif self.exchange_name in SUPPORTED_EXCHANGES:
            out = self._other_to_cpc(cpc, tkn0, tkn1)
        else:
            raise NotImplementedError(f"Exchange {self.exchange_name} not implemented.")

        return out

    def _other_to_cpc(self, cpc: ConstantProductCurve, tkn0: Token, tkn1: Token) -> List[Any]:
        """
        constructor: from Uniswap V2 pool (see class docstring for other parameters)

        :param cpc: ConstantProductCurve class
        :param tkn0: Token 0
        :param tkn1: Token 1

        :x_tknb:    current pool liquidity in token x (base token of the pair)*
        :y_tknq:    current pool liquidity in token y (quote token of the pair)*
        :k:         uniswap liquidity parameter (k = xy)*

        *exactly one of k,x,y must be None; all other parameters must not be None;
        a reminder that x is TKNB and y is TKNQ
        """
        arg_type = Decimal

        # convert tkn0_balance and tkn1_balance to Decimal from wei
        tkn0_balance = self.convert_decimals(self.tkn0_balance, tkn0.decimals)
        tkn1_balance = self.convert_decimals(self.tkn1_balance, tkn1.decimals)

        # create a typed-dictionary of the arguments
        typed_args = {
            "x_tknb": tkn0_balance,
            "y_tknq": tkn1_balance,
            "pair": self.pair_name.replace("ETH-EEeE", "WETH-6Cc2"),
            "fee": self.fee,
            "cid": self.cid,
            "descr": self.descr,
            "params": {
                "exchange": self.exchange_name,
            },
        }
        return [cpc.from_univ2(**self._validate_arg_types(typed_args))]

    def _carbon_to_cpc(
        self, cpc: ConstantProductCurve, tkn0, tkn1
    ) -> ConstantProductCurve:
        """
        constructor: from a single Carbon order (see class docstring for other parameters)*

        :yint:      current pool y-intercept**
        :y:         current pool liquidity in token y
        :pa:        fastlane_bot price range left bound (higher price in dy/dx)
        :pb:        fastlane_bot price range right bound (lower price in dy/dx)
        :A:         alternative to pa, pb: A = sqrt(pa) - sqrt(pb) in dy/dy
        :B:         alternative to pa, pb: B = sqrt(pb) in dy/dy
        :tkny:      token y
        :isdydx:    if True prices in dy/dx, if False in quote direction of the pair

        *Note that ALL parameters are mandatory, except that EITHER pa, bp OR A, B
        must be given but not both; we do not correct for incorrect assignment of
        pa and pb, so if pa <= pb IN THE DY/DX DIRECTION, MEANING THAT THE NUMBERS
        ENTERED MAY SHOW THE OPPOSITE RELATIONSHIP, then an exception will be raised

        **note that the result does not depend on yint, and for the time being we
        allow to omit yint (in which case it is set to y, but this does not make
        a difference for the result)
        """

        # if idx == 0, use the first curve, otherwise use the second curve. change the numerical values to Decimal
        arg_type = Decimal
        lst = []
        for i in [0, 1]:
            pair = self.pair_name.replace("ETH-EEeE", "WETH-6Cc2")
            S = Decimal(self.A_1) if i == 0 else Decimal(self.A_0)
            B = Decimal(self.B_1) if i == 0 else Decimal(self.B_0)
            y = Decimal(self.y_1) if i == 0 else Decimal(self.y_0)
            z = yint = Decimal(self.z_1) if i == 0 else Decimal(self.z_0)

            encoded_order = EncodedOrder(
                **{
                    "token": self.pair_name.split("/")[i].replace(
                        "ETH-EEeE", "WETH-6Cc2"
                    ),
                    "A": S,
                    "B": B,
                    "y": y,
                    "z": z,
                }
            )

            def decimal_converter(idx):
                if idx == 0:
                    dec0 = tkn0.decimals
                    dec1 = tkn1.decimals
                else:
                    dec0 = tkn1.decimals
                    dec1 = tkn0.decimals
                return Decimal(10 ** (dec0 - dec1))

            decimal_converter = decimal_converter(i)

            p_start = Decimal(encoded_order.p_start) * decimal_converter
            p_end = Decimal(encoded_order.p_end) * decimal_converter
            yint = Decimal(yint) / (
                Decimal("10") ** [tkn1.decimals, tkn0.decimals][i]
            )
            y = Decimal(y) / (
                Decimal("10") ** [tkn1.decimals, tkn0.decimals][i]
            )

            tkny = 1 if i == 0 else 0
            typed_args = {
                "cid": f"{self.cid}-{i}",
                "yint": yint,
                "y": y,
                "pb": p_end,
                "pa": p_start,
                "tkny": self.pair_name.split("/")[tkny].replace(
                    "ETH-EEeE", "WETH-6Cc2"
                ),
                "pair": self.pair_name.replace("ETH-EEeE", "WETH-6Cc2"),
                "params": {"exchange": self.exchange_name},
                "fee": self.fee,
                "descr": self.descr,
            }
            lst.append(cpc.from_carbon(**self._validate_arg_types(typed_args)))
        return lst

    def _univ3_to_cpc(self, cpc: ConstantProductCurve, tkn0: Token, tkn1: Token) -> List[Any]:
        """
        Preprocesses a Uniswap V3 pool params in order to create a ConstantProductCurve instance for optimization.

        :param arg_type: The type of numerical values. (Decimal or float)
        :param cpc: The ConstantProductCurve class.
        :param tkn0: The token0 of the pool.
        :param tkn1: The token1 of the pool.

        :return: ConstantProductCurve
            :k:        pool constant k = xy [x=k/y, y=k/x]
            :x:        (virtual) pool state x (virtual number of base tokens for sale)
            :x_act:    actual pool state x (actual number of base tokens for sale)
            :y_act:    actual pool state y (actual number of quote tokens for sale)
            :pair:     tkn_address pair in slash notation ("TKNB/TKNQ"); TKNB is on the x-axis, TKNQ on the y-axis
            :cid:      unique id (optional)
            :fee:      fee (optional); eg 0.01 for 1%
            :descr:    description (optional; eg. "UniV3 0.1%")
            :params:   additional parameters (optional)

        """

        univ3_helper = UniV3Helper(
            contract_initialized=True,
            fee=self.fee,
            tick=self.tick,
            tick_spacing=self.tick_spacing,
            sqrt_price_q96=self.sqrt_price_q96,
            liquidity=self.liquidity,
            tkn0_decimal=tkn0.decimals,
            tkn1_decimal=tkn1.decimals,
        )

        P_marg = univ3_helper.Pmarg
        P_a = univ3_helper.Pa
        P_b = univ3_helper.Pb
        L = univ3_helper.L

        # create a typed-dictionary of the arguments
        typed_args = {
            "cid": self.cid,
            "Pmarg": P_marg,
            "uniL": L,
            "uniPa": P_a,
            "uniPb": P_b,
            "pair": self.pair_name.replace("ETH-EEeE", "WETH-6Cc2"),
            "params": {"exchange": self.exchange_name},
            "fee": self.fee,
            "descr": self.descr,
        }
        return [cpc.from_univ3(**self._validate_arg_types(typed_args))]




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



