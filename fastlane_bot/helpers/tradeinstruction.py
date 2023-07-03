"""
Helpers for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.2"
__DATE__="02/May/2023"

from dataclasses import dataclass
from typing import Union, Any
from _decimal import Decimal
from fastlane_bot.events.interface import Token, Pool


@dataclass
class TradeInstruction:
    """
    A class that handles the conversion of token decimals for the bot.

    Parameters
    ----------
    cid: str
        The pool unique ID
    tknin: str
        The input token key (e.g. 'DAI-1d46')
    amtin: int or Decimal or float
        The input amount.
    tknout: str
        The output token key (e.g. 'DAI-1d46')
    amtout: int or Decimal or float
        The output amount.
    cid_tkn: str
        If the curve is a Carbon curve, the cid will have a "-1" or "-0" to denote which side of the strategy the trade is on.
        This parameter is used to remove the "-1" or "-0" from the cid.
    raw_txs: str
    pair_sorting: str

    Attributes
    ----------
    
    TODO -- DOCSTRING OUT OF DATE 
    _tknin_address: str
        The input token address.
    _tknin_decimals: int
        The input token decimals.
    _amtin_wei: int
        The input amount in wei.
    _amtin_decimals: Decimal
        The input amount in decimals.
    _tknout_address: str
        The output token address.
    _tknout_decimals: int
        The output token decimals.
    _amtout_wei: int
        The output amount in wei.
    _amtout_decimals: Decimal
        The output amount in decimals.
    _is_carbon: bool
        Whether the curve is a Carbon curve.

    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    ConfigObj: Any
    cid: str
    tknin: str
    amtin: Union[int, Decimal, float]
    tknout: str
    amtout: Union[int, Decimal, float]
    pair_sorting: str = None
    raw_txs: str = None
    custom_data: str = ''
    db: any = None
    tknin_dec_override: int = None   # for testing to not go to the database
    tknout_dec_override: int = None  # ditto
    tknin_addr_override: str = None  # ditto
    tknout_addr_override: str = None # ditto
    exchange_override: str = None    # ditto
    _amtin_wei: int = None
    _amtout_wei: int = None

    @property
    def tknin_key(self) -> str:
        """
        The input token key (e.g. 'DAI-1d46')
        """
        return self.tknin

    @property
    def tknout_key(self) -> str:
        """
        The output token key (e.g. 'DAI-1d46')
        """
        return self.tknout

    def __post_init__(self):
        """
        Use the database session to get the token addresses and decimals based on the Pool.cid and Token.key
        """
        self._cid_tkn: str = None
        self._is_carbon = self._check_if_carbon()
        
        if self.tknin_dec_override is None:
            TokenIn = self.db.get_token(key =self.tknin)
            self._tknin_address = TokenIn.address
            self._tknin_decimals = int(TokenIn.decimals)
        else:
            self._tknin_address = self.tknin_addr_override
            self._tknin_decimals = self.tknin_dec_override

        if self._amtin_wei is None:
            self._amtin_wei = self._convert_to_wei(self.amtin, self._tknin_decimals)

        self._amtin_decimals = self._convert_to_decimals(
            self.amtin, self._tknin_decimals
        )
        self._amtin_quantized = self._quantize(
            self._amtin_decimals, self._tknin_decimals
        )
        
        if self.tknout_dec_override is None:
            TokenOut = self.db.get_token(key =self.tknout)
            self._tknout_address = TokenOut.address
            self._tknout_decimals = int(TokenOut.decimals)
        else:
            self._tknout_address = self.tknout_addr_override
            self._tknout_decimals = self.tknout_dec_override
            
        if self._amtout_wei is None:            
            self._amtout_wei = self._convert_to_wei(self.amtout, self._tknout_decimals)

        self._amtout_decimals = self._convert_to_decimals(
            self.amtout, self._tknout_decimals
        )
        self._amtout_quantized = self._quantize(
            self._amtout_decimals, self._tknout_decimals
        )
        if self.raw_txs is None:
            self.raw_txs = "[]"
        if self.pair_sorting is None:
            self.pair_sorting = ""
        if self.exchange_override is None:
            self._exchange_name = self.db.get_pool(cid=self.cid.split('-')[0]).exchange_name
        else:
            self._exchange_name = self.exchange_override
        self._exchange_id = self.ConfigObj.EXCHANGE_IDS[self._exchange_name]

    @property
    def platform_id(self) -> int:
        """
        The exchange ID. (0 = Bancor V2, 1 = Bancor V3, 2 = Uniswap V2, 3 = Uniswap V3, 4 = Sushiswap V2, 5 = Sushiswap, 6 = Carbon)
        """
        return self._exchange_id

    @property
    def exchange_name(self) -> str:
        """
        The exchange name.
        """
        return self._exchange_name

    @staticmethod
    def _quantize(amount: Decimal, decimals: int) -> Decimal:
        """
        Quantizes the amount based on the token decimals.

        Parameters
        ----------
        amount: Decimal
            The amount.
        decimals: int
            The token decimals.

        Returns
        -------
        Decimal
            The quantized amount.
        """
        # print(f"[_quantize], amount: {amount}, type = {type(amount)}, decimals: {decimals}, type {type(decimals)}")

        if "." not in str(amount):
            return Decimal(str(amount))
        amount = format(amount, 'f')
        amount_num = str(amount).split(".")[0]
        amount_dec = str(amount).split(".")[1]
        # print(f"[_quantize], amount_dec: {amount_dec}, type = {type(amount_dec)}")
        amount_dec = str(amount_dec)[:int(decimals)]
        # print(f"[_quantize], amount_dec: {amount_dec}, type = {type(amount_dec)}")
        try:
            return Decimal(f"{str(amount_num)}.{amount_dec}")
        except Exception as e:
            #print("Error quantizing amount: ", f"{str(amount_num)}.{amount_dec}")
            pass



    def _get_token_address(self, token_key: str) -> str:
        """
        Gets the token address based on the token key.

        Parameters
        ----------
        token_key: str
            The token key (e.g. 'DAI-1d46')

        Returns
        -------
        str
            The token address.
        """
        return self._get_token(token_key).address

    def _get_token_decimals(self, token_key: str) -> int:
        """
        Gets the token decimals based on the token key.

        Parameters
        ----------
        token_key: str
            The token key (e.g. 'DAI-1d46')

        Returns
        -------
        int
            The token decimals.
        """
        return self._get_token(token_key).decimals

    def _get_token(self, token_key: str) -> Token:
        """
        Gets the token object based on the token key.

        Parameters
        ----------
        token_key: str
            The token key (e.g. 'DAI-1d46')

        Returns
        -------
        Token
            The token object.
        """

        return self.db.get_token(key=token_key)

    def _get_pool(self) -> Pool:
        """
        Gets the pool object based on the pool cid.

        Returns
        -------
        Pool
            The pool object.
        """
        return self.db.get_pool(cid=self.cid)

    @staticmethod
    def _convert_to_wei(amount: Union[int, Decimal, float], decimals: int) -> int:
        """
        Converts the amount to wei.

        Parameters
        ----------
        amount: int, Decimal or float
            The amount.
        decimals: int
            The token decimals.

        Returns
        -------
        int
            The amount in wei.
        """
        return int(amount * 10**decimals)

    @staticmethod
    def _convert_to_decimals(
        amount: Union[int, Decimal, float], decimals: int
    ) -> Decimal:
        """
        Converts the amount to decimals.

        Parameters
        ----------
        amount: int, Decimal or float
            The amount.
        decimals: int
            The token decimals.

        Returns
        -------
        Decimal
            The amount in decimals.
        """
        return Decimal(amount) / Decimal(10**decimals)

    def _check_if_carbon(self) -> bool:
        """
        Checks if the curve is a Carbon curve.

        Returns
        -------
        bool
            Whether the curve is a Carbon curve.
        """
        if "-" in self.cid:
            self._cid_tkn = self.cid.split("-")[1]
            self.cid = self.cid.split("-")[0]
            return True
        return False

    @property
    def cid_tkn(self) -> str:
        """
        The token cid.
        """
        return self._cid_tkn

    @property
    def tknin_address(self) -> str:
        """
        The input token address.
        """
        return self._tknin_address

    @property
    def tknin_decimals(self) -> int:
        """
        The input token decimals.
        """
        return self._tknin_decimals

    @property
    def amtin_wei(self) -> int:
        """
        The input amount in wei.
        """
        return self._amtin_wei

    @property
    def amtin_decimals(self) -> Decimal:
        """
        The input amount in decimals.
        """
        return self._amtin_decimals

    @property
    def tknout_address(self) -> str:
        """
        The output token address.
        """
        return self._tknout_address

    @property
    def tknout_decimals(self) -> int:
        """
        The output token decimals.
        """
        return self._tknout_decimals

    @property
    def amtout_wei(self) -> int:
        """
        The output amount in wei.
        """
        return self._amtout_wei

    @property
    def amtout_decimals(self) -> Decimal:
        """
        The output amount in decimals.
        """
        return self._amtout_decimals

    @property
    def is_carbon(self) -> bool:
        """
        Whether the curve is a Carbon curve.
        """
        return self._is_carbon

    @property
    def pool(self) -> Pool:
        """
        The pool object.
        """
        return self._get_pool()

    @property
    def token_in(self) -> Token:
        """
        The input token object.
        """
        return self._get_token(self.tknin)

    @property
    def token_out(self) -> Token:
        """
        The output token object.
        """
        return self._get_token(self.tknout)

    @property
    def amtin_quantized(self) -> Decimal:
        """
        Returns
        -------
        Decimal
            The quantized input amount.
        """
        return self._amtin_quantized

    @property
    def amtout_quantized(self) -> Decimal:
        """
        Returns
        -------
        Decimal
            The quantized output amount.
        """
        return self._amtout_quantized
