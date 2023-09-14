"""
Fastlane bot config -- logger
"""
__VERSION__ = "1.0"
__DATE__ = "03/May 2023"

import os
import time

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

    _log_path = None

    def get_logger(self, loglevel: str, logging_path: str = None) -> logging.Logger:
        """
        Returns a logger with the specified logging level

        Args:
            loglevel (str): The desired logging level.
            logging_path (str): The path to the logging directory.

        Returns:
            logging.Logger: A logger object with the specified logging level.
        """
        log_level = getattr(logging, loglevel.upper())
        logger = logging.getLogger("fastlane")
        logger.setLevel(log_level)

        # Generate timestamped directory
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        if logging_path is not None and logging_path != "":
            log_directory = f"{logging_path}/logs/{timestamp}"
        else:
            log_directory = f"logs/{timestamp}"

        os.makedirs(log_directory, exist_ok=True)

        # Create a file handler to write to a .txt file in the timestamped directory
        log_filename = os.path.join(log_directory, "bot.log")
        self._log_path = log_filename  # Store the log file path for later use
        handler = logging.FileHandler(log_filename)

        # Create a stream handler to write to the terminal
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)

        handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s:%(levelname)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(stream_handler)

        logger.info("")
        logger.info("**********************************************")
        logger.info(f"The logging path is set to: {self._log_path}")
        logger.info("**********************************************")
        logger.info("")

        return logger

    @property
    def log_path(self):
        """Returns the path to the log file"""
        return self._log_path

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
    def new(cls, *, logger=None, loglevel=None, logging_path=None, **kwargs):
        """
        Return a new ConfigLogger.
        """
        if logger is None:
            logger = S.LOGGER_DEFAULT

        if logger == S.LOGGER_DEFAULT:
            return _ConfigLoggerDefault(_direct=False, loglevel=loglevel, logging_path=logging_path, **kwargs)
        else:
            raise ValueError(f"Unknown logger: {logger}")

    def __init__(self, loglevel=None, logging_path=None, **kwargs):
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
        self._logger = self.get_logger(self.LOGLEVEL, logging_path=logging_path)


class _ConfigLoggerDefault(ConfigLogger):
    """
    Fastlane bot config -- logger
    """
    pass


    