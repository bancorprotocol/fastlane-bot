"""
Fastlane bot config -- logger
"""
__VERSION__ = "1.0"
__DATE__ = "03/May 2023"

from .base import ConfigBase
from . import selectors as S
import logging

# NOTE: THIS WHOLE LOGGING BUSINESS IS A BIT CONVOLUTED, SO AT ONE POINT
# WE MAY CONSIDER CLEANING IT UP

class ConfigLogger(ConfigBase):
    """
    Fastlane bot config -- logger
    
    :loglevel:    LOGLEVEL_DEBUG, LOGLEVEL_INFO (default), LOGLEVEL_WARNING, LOGLEVEL_ERROR
    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    LOGGER_DEFAULT = S.LOGGER_DEFAULT
    LOGLEVEL_DEBUG = S.LOGLEVEL_DEBUG
    LOGLEVEL_INFO = S.LOGLEVEL_INFO
    LOGLEVEL_WARNING = S.LOGLEVEL_WARNING
    LOGLEVEL_ERROR = S.LOGLEVEL_ERROR
    LOGLEVEL = S.LOGLEVEL_INFO
    
    def get_logger(self, loglevel: str) -> logging.Logger:
        """
        Returns a logger with the specified logging level

        Args:
            loglevel (str): The desired logging level.

        Returns:
            logging.Logger: A logger object with the specified logging level.
        """
        log_level = getattr(logging, loglevel.upper())
        logger = logging.getLogger("fastlane")
        logger.setLevel(log_level)
        #print(f"[get_logger] {loglevel} {log_level}")
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s:%(levelname)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    @property
    def logger(self):
        return self._logger
    
    def debug(self, *args, **kwargs):
        """calls logger.debug()"""
        return self.logger.debug(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        """calls logger.info()"""
        return self.logger.info(*args, **kwargs)
    
    def warning(self, *args, **kwargs):
        """calls logger.warning()"""
        return self.logger.warning(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        """calls logger.error()"""
        return self.logger.error(*args, **kwargs)
    
    @classmethod
    def new(cls, *, logger=None, loglevel=None, **kwargs):
        """
        Return a new ConfigLogger.
        """
        if logger is None:
            logger = S.LOGGER_DEFAULT
        
        if logger == S.LOGGER_DEFAULT:
            return _ConfigLoggerDefault(_direct=False, loglevel=loglevel, **kwargs)
        else:
            raise ValueError(f"Unknown logger: {logger}")
        
    def __init__(self, loglevel=None, **kwargs):
        super().__init__(**kwargs)
        #print("[ConfigLogger]", loglevel, self.LOGLEVEL)
        if not loglevel is None:
            assert loglevel in {
                self.LOGLEVEL_DEBUG, 
                self.LOGLEVEL_INFO, 
                self.LOGLEVEL_WARNING, 
                self.LOGLEVEL_ERROR
            }, f"unknown loglevel {loglevel}"
            self.LOGLEVEL = loglevel
        self._logger = self.get_logger(self.LOGLEVEL)


class _ConfigLoggerDefault(ConfigLogger):
    """
    Fastlane bot config -- logger
    """
    pass
        

    
