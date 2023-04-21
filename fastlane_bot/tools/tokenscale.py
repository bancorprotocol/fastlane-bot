"""
estimating the scale of the token price in USD

NOTE: this class is not part of the Bancor Simulator API, and breaking changes may occur at any time

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__ = "07/Apr/2022"

from dataclasses import dataclass, field, asdict, InitVar


class TokenScaleBase:
    """
    the "scale" of a token, ie the number of tokens per USD, typically rounded to the next power of 10
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    DEFAULT_SCALE = 1e-2

    def scale(self, token):
        """
        returns the scale of the token*

        :tkn: the token whose scale is to be returned

        *the "scale" of a token the number of tokens per USD, typically rounded
        to the next power of 10; every token MUST have a scale; if the _scale
        function (that implements this method) returns None, DEFAULT_SCALE is returned
        """
        result = self._scale(token)
        if result is None:
            result = self.DEFAULT_SCALE
        return result

    def _scale(self, token):
        """
        implements the scale method in derived classes
        """
        raise NotImplementedError("{self.__class__.__name__} did not implement _scale")

    def __call__(self, token):
        """alias for scale"""
        return self.scale(token)


class TokenScale1(TokenScaleBase):
    """trivial implementation of TokenScaleBase returning unit scale for all tokens"""

    DEFAULT_SCALE = 1e00

    def _scale(self, token):
        """implementation of _scale for TokenScale1 class: always returns unit scale"""
        return self.DEFAULT_SCALE


@dataclass
class TokenScale(TokenScaleBase):
    """
    implements the `TokenScaleBase` interface using a dictionary
    """

    scale_dct: dict = field(default_factory=dict)

    @classmethod
    def from_tokenscales(cls, **scale):
        """alternative constructor with the scale in kwargs"""
        return cls(scale_dct=scale)

    def add_scale(self, token, scale):
        """
        adds (or replaces) a scale for a token
        """
        self.scale_dct[token] = scale

    def _scale(self, token):
        """implementation of _scale for TokenScale class (reading from dict)"""
        return self.scale_dct.get(token, None)


TokenScaleData = TokenScale.from_tokenscales(
    USDC=1e00,
    USDT=1e00,
    LINK=1e01,
    AAVE=1e02,
    ETH=1e03,
    WETH=1e03,
    WBTC=1e04,
    BTC=1e04,
    BNT=1e00,
    SUSHI=1e00,
    UNI=1e01,
)

TokenScale1Data = TokenScale1()
