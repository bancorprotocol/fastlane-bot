"""
Base configuration class for the fastlane_bot application.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT
"""
__VERSION__ = "1.1"
__DATE__ = "30/Apr 2023"


class ConfigBase:
    """
    Base configuration class.

    Explanation:
        This class serves as the base class for other configuration classes. It provides common functionality such as initialization and representation.

    Args:
        _direct: Whether the class is instantiated directly. Defaults to True.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Examples:
        # Instantiate a subclass of ConfigBase
        class MyConfig(ConfigBase):
            pass

        config = MyConfig()
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def __init__(self, _direct: bool = True, **kwargs) -> None:
        """
        Initializes the configuration object.

        Args:
            _direct: Whether the class is instantiated directly. Defaults to True.
            **kwargs: Additional keyword arguments.

        Returns:
            None

        Raises:
            AssertionError: If _direct is True.

        Examples:
            # Instantiate a subclass of ConfigBase
            class MyConfig(ConfigBase):
                pass

            config = MyConfig()
        """

        assert (
            _direct == False
        ), f"Must instantiate a subclass of {self.__class__.__name__} via new()"
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        """
        Returns a string representation of the object.

        Returns:
            str: The string representation of the object.
        """

        return f"{self.__class__.__name__}()"
