"""
Base configuration class for the fastlane_bot application.
"""
__VERSION__ = "1.1"
__DATE__ = "30/Apr 2023"

class ConfigBase():
    """
    Base configuration class for the fastlane_bot application.
    
    :kwargs:    keyword arguments to set as additional attributes
    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    def __init__(self, _direct=True, **kwargs):
        assert _direct==False, f"Must instantiate a subclass of {self.__class__.__name__} via new()"
        for k, v in kwargs.items():
            # if hasattr(self, k):
            #     print("[{0.__class__.__name__}:__init__] overriding {1}={2}".format(self, k, v))
            # else:
            #     print("[{0.__class__.__name__}:__init__] setting {1}={2}".format(self, k, v))    
            setattr(self, k, v)
                
        #print(f"[{self.__class__.__name__}:__init__] complete")
    
    def __repr__(self):
        #print("{0.__class__.__name__}({1})".format(self, ", ".join("{0}={1!r}".format(k, v) for k, v in self.__dict__.items())))
        return f"{self.__class__.__name__}()"