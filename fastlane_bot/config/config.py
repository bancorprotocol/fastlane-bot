"""
Fastlane bot configuration object -- main object
"""
__VERSION__ = "1.0-BETA4"
__DATE__ = "26/Apr 2023"

from dataclasses import dataclass, field, InitVar, asdict
#from .base import ConfigBase
from . import network as network_, db as db_, logger as logger_, provider as provider_

@dataclass
class Config():
    """
    Fastlane bot configuration object
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    network: network_.ConfigNetwork = field(default=None)
    db: db_.ConfigDB = field(default=None)
    #fastlane: fastlane_.ConfigFastlane = field(default=None)
    logger: logger_.ConfigLogger = field(default=None)
    provider: provider_.ConfigProvider = field(default=None)
    
    def is_config_item(self, item):
        """returns True if item is a (possible) configuration item [uppercase, numbers, underscore; len>2]"""
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