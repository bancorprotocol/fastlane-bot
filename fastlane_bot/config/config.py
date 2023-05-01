"""
Fastlane bot configuration object -- main object
"""
__VERSION__ = "1.0-BETA7"
__DATE__ = "30/Apr 2023"

from dataclasses import dataclass, field, InitVar, asdict
#from .base import ConfigBase
from . import network as network_, db as db_, logger as logger_, provider as provider_
from .cloaker import CloakerL
from . import selectors as S

@dataclass
class Config():
    """
    Fastlane bot configuration object
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    network: network_.ConfigNetwork = field(default=None)
    db: db_.ConfigDB = field(default=None)
    logger: logger_.ConfigLogger = field(default=None)
    provider: provider_.ConfigProvider = field(default=None)
    
    
    # NETWORK_MAINNET = S.NETWORK_MAINNET
    # NETWORK_TENDERLY = S.NETWORK_TENDERLY
    # DATABASE_POSTGRES = S.DATABASE_POSTGRES
    # DATABASE_TESTING = S.DATABASE_TESTING
    CONFIG_UNITTEST = "unittest"
    CONFIG_TENDERLY = "tenderly"
    CONFIG_MAINNET = "mainnet"
    @classmethod
    def new(cls, *, config=None, **kwargs):
        """
        Alternative constructor: create and return new Config object
        
        :config:    CONFIG_MAINNET(default), CONFIG_TENDERLY, CONFIG_UNITTEST
        """
        if config is None:
            config = cls.CONFIG_MAINNET
            
        if config == cls.CONFIG_MAINNET:
            C_nw = network_.ConfigNetwork.new(network=S.NETWORK_MAINNET)
            return cls(network=C_nw, **kwargs)
        elif config == cls.CONFIG_TENDERLY:
            C_db = db_.ConfigDB.new(db=S.DATABASE_POSTGRES, POSTGRES_DB="tenderly")
            C_nw = network_.ConfigNetwork.new(network=S.NETWORK_TENDERLY)
            return cls(db=C_db, network=C_nw, **kwargs)
        elif config == cls.CONFIG_UNITTEST:
            C_db = db_.ConfigDB.new(db=S.DATABASE_UNITTEST)
            C_nw = network_.ConfigNetwork.new(network=S.NETWORK_MAINNET)
            # C_pr = provider_.ConfigProvider.new(network=C_nw, provider=S.PROVIDER_UNITTEST)
            return cls(db=C_db, network=C_nw, **kwargs)
        raise ValueError(f"Invalid config: {config}")
    
    def is_config_item(self, item):
        """returns True if item is a (possible) configuration item [uppercase, numbers, underscore; len>2]"""
        #print("[is_config_item]", item)
        if item in {"w3", "connection"}:
            return True
        if len(item)<3:
            return False
        if not item[0].isupper():
            return False
        for c in item[1:]:
            if not (item.isupper() or item.isnumeric() or item == "_"):
                return False
        return True
    
    def get_attribute_from_config(self, name: str):
        """
        gets the attribute from the constituent config objects, raises if not found
        """
        for obj in [self.network, self.db, self.provider, self.logger]:
            if hasattr(obj, name):
                return getattr(obj, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
    def __getattr__(self, name: str):
        """
        If of type attribute, return it.
        """
        if self.is_config_item(name):
            return self.get_attribute_from_config(name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __post_init__(self):
        """
        Post-initialization initialization.
        """
        if self.network is None:
            self.network = network_.ConfigNetwork.new(network_.ConfigNetwork.NETWORK_ETHEREUM)
        assert issubclass(type(self.network), network_.ConfigNetwork)
        
        if self.db is None:
            self.db = db_.ConfigDB.new(db_.ConfigDB.DATABASE_POSTGRES)
        assert issubclass(type(self.db), db_.ConfigDB)
        
        # if self.fastlane is None:
        #     self.fastlane = fastlane_.ConfigFastlane.new()
        # assert issubclass(type(self.fastlane), fastlane_.ConfigFastlane)
        
        if self.logger is None:
            self.logger = logger_.ConfigLogger.new()
        assert issubclass(type(self.logger), logger_.ConfigLogger)
        
        if self.provider is None:
            self.provider = provider_.ConfigProvider.new(self.network)
        assert issubclass(type(self.provider), provider_.ConfigProvider)
        
        assert self.network is self.provider.network, f"Network mismatch: {self.network} != {self.provider.network}"
        
    VISIBLE_FIELDS = "network, db, logger, provider, w3, ZERO_ADDRESS"    
    def cloaked(self, incl=None, excl=None):
        """
        returns a cloaked version of the object
        
        :incl:  fields to _include_ in the cloaked version (plus those in VISIBLE_FIELDS)
        :excl:  fields to _exclude_ from the cloaked version
        """
        visible = self.VISIBLE_FIELDS
        if isinstance(visible, str):
            visible = (x.strip() for x in visible.split(","))
        visible = set(visible)
        
        if isinstance(incl, str):
            incl = (x.strip() for x in incl.split(","))
        elif incl is None:
            incl = []
        visible |= set(incl)
        
        if isinstance(excl, str):
            excl = (x.strip() for x in excl.split(","))
        elif excl is None:
            excl = []
        visible -= set(excl)
        
        return CloakerL(self, visible)
    
    
        