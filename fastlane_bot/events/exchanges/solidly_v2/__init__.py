from .base import SolidlyV2 as SolidlyV2Base
from .velocimeter_v2 import VelocimeterV2
from .equalizer_v2 import EqualizerV2
from .velodrome_v2 import VelodromeV2
from .scale_v2 import ScaleV2
from .cleopatra_v2 import CleopatraV2
from .lynex_v2 import LynexV2
from .nile_v2 import NileV2
from .xfai_v0 import XFaiV2
from .archly_v2 import ArchlyV2


class SolidlyV2(SolidlyV2Base):
    def __new__(cls, **kwargs):
        return {
            "velocimeter_v2": VelocimeterV2,
            "equalizer_v2": EqualizerV2,
            "aerodrome_v2": VelodromeV2,
            "velodrome_v2": VelodromeV2,
            "scale_v2": ScaleV2,
            "cleopatra_v2": CleopatraV2,
            "stratum_v2": VelocimeterV2,
            "lynex_v2": LynexV2,
            "nile_v2": NileV2,
            "xfai_v0": XFaiV2,
            "archly_v2": ArchlyV2,
        }[kwargs["exchange_name"]](**kwargs)
