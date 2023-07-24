"""
cloaking access to python files

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0-BETA1"
__DATE__ = "26/Apr 2023"

from dataclasses import dataclass

@dataclass
class ShieldedAttribute():
    """returned instead of the attribute value for shielded attributes"""
    attr: str = None
    exists: bool = None
    
class Cloaker():
    """
    Cloaking access to python files -- Base class
    
    :cloaked_item:    the item to cloak
    
    USAGE
    
    This class contains two methods, plus the associated implementation methods
    that can be overridden in subclasses, that determine its behaviour:
    
    - is_visible:   if the attribute exists and visible it is passed through
    - is_shielded:  this is called if either the attribute does not exist, or it is
                    not visible (second parameter); if it returns True then the
                    result is provided as None, otherwise an AttributeError is raised
    """
    def __init__(self, cloaked_item):
        self._cloaked_item = cloaked_item
        
    def _is_visible(self, attr_name):
        """
        whether the attribute is visible (wrapper; calls ___is_visible)
        
        :attr_name:    name of the attribute to test
        :returns:      True if visible, False otherwise
        """
        return self._is_visible_(attr_name)
    
    def _is_visible_(self, attr_name):
        """
        implementation function of _is_visible [CloakerBase]
        
        visible iff not starting with "_"
        """
        #print("[Cloaker:_is_visible_]", attr_name)
        return not attr_name.startswith("_")
    
    def _is_shielded(self, attr_name, attr_exists):
        """
        whether the (invisible) attribute is None (wrapper; calls ___is_shielded)
        
        :attr_name:     name of the attribute to test
        :attr_exists:   whether the attribute exists on the cloaked item
                        (if it exists then visible = False)
        :returns:       True if None, False otherwise
        """
        return self._is_shielded_(attr_name, attr_exists)
    
    def _is_shielded_(self, attr_name, attr_exists):
        """
        implementation function of _is_shielded [CloakerBase]
        
        None iff it exists
        """
        #print("[__is_shielded]", attr_name)
        return attr_exists
    
    _ShieldedAttribute = ShieldedAttribute
    _SHIELDF = ShieldedAttribute
    def __getattr__(self, attr_name):
        if hasattr(self._cloaked_item, attr_name):
            #print("[CloakerBase] has attribute", attr_name)
            if self._is_visible(attr_name):
                return getattr(self._cloaked_item, attr_name)
            if self._is_shielded(attr_name, True):
                return self._SHIELDF(attr_name, True)
        else:
            #print("[CloakerBase] does NOT have attribute", attr_name)
            if self._is_shielded(attr_name, False):
                return self._SHIELDF(attr_name, False)
        raise AttributeError(f"Cloaked[{self._cloaked_item.__class__.__name__}] has no attribute '{attr_name}'")

class CloakerL(Cloaker):
    """Cloaker with (visible) set of attributes"""
    def __init__(self, cloaked_item, visible):
        super().__init__(cloaked_item)
        if isinstance(visible, str):
            visible = (x.strip() for x in visible.split(","))
        self._visible = set(visible)
        
    def _is_visible_(self, attr_name):
        """
        visible iff in visible set
        """
        #print("[CloakerL:_is_visible_]", attr_name)
        return attr_name in self._visible
    
    def _is_shielded_(self, attr_name, attr_exists):
        """always shielded"""
        return True