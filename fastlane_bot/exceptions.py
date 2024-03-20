class ReadOnlyException(Exception):
    def __init__(self, filepath):
        self.filepath = filepath

    def __str__(self):
        return (f"tokens.csv does not exist at {self.filepath}. Please run the bot without the `read_only` flag to "
                f"create this file.")


class AsyncUpdateRetryException(Exception):
    """
    Exception raised when async_update_pools_from_contracts fails and needs to be retried.
    """
    pass


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


