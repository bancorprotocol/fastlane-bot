"""
Collects exceptions used by the code

NOTE: Use of this module is not consistent throughout the codebase. In fact, most exceptions
are defined locally either a module or at class level. Also this file is relatively short
and we should review whether this design makes sense (TODO)

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
class ReadOnlyException(Exception):
    def __init__(self, filepath):
        self.filepath = filepath

    def __str__(self):
        return (f"tokens.csv does not exist at {self.filepath}. Please run the bot without the `read_only` flag to "
                f"create this file.")


class FlashloanUnavailableException(Exception):
    """
    Exception raised when not configured to use self_fund on a blockchain that does not support Flashloans.
    """
    pass


class FlashloanTokenException(Exception):
    """
    Exception raised due to an incompatible Flashloan token combination.
    """
    pass


