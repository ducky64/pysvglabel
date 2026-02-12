from enum import Enum
from typing import Tuple

from .units import LengthDimension, px


class Align(Enum):
    TOP_LEFT = (0,)
    TOP = (1,)
    TOP_RIGHT = (2,)
    LEFT = (3,)
    CENTER = (4,)
    RIGHT = (5,)
    BOT_LEFT = (6,)
    BOT = (7,)
    BOT_RIGHT = 8

    @staticmethod
    def to_transform(
        align: "Align",
        src_size: Tuple[LengthDimension, LengthDimension],
        dst_size: Tuple[LengthDimension, LengthDimension],
    ) -> Tuple[LengthDimension, LengthDimension]:
        """Returns the translation to align src within dst for the given alignment, with (0, 0) being
        src and dst aligned to the top left.
        :return: alignment translation as (dx, dy)
        """
        # handle X transform
        if align in [Align.TOP_LEFT, Align.LEFT, Align.BOT_LEFT]:  # left align
            dx = 0 * px
        elif align in [Align.TOP, Align.CENTER, Align.BOT]:  # center align
            dx = (dst_size[0] - src_size[0]) / 2
        elif align in [Align.TOP_RIGHT, Align.RIGHT, Align.BOT_RIGHT]:  # right align
            dx = dst_size[0] - src_size[0]
        else:
            raise ValueError(f"unknown alignment {align}")

        # handle Y transform
        if align in [Align.TOP_LEFT, Align.TOP, Align.TOP_RIGHT]:  # top align
            dy = 0 * px
        elif align in [Align.LEFT, Align.CENTER, Align.RIGHT]:  # center align
            dy = (dst_size[1] - src_size[1]) / 2
        elif align in [Align.BOT_LEFT, Align.BOT, Align.BOT_RIGHT]:  # bottom align
            dy = dst_size[1] - src_size[1]
        else:
            raise ValueError(f"unknown alignment {align}")

        return dx, dy
