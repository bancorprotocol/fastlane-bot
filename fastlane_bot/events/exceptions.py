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
