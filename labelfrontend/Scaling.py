from enum import Enum
from typing import Tuple

from .units import LengthDimension, px


class Scaling(Enum):
  NONE = 1,
  FIT = 2

  @staticmethod
  def to_transform(scaling: 'Scaling', src_size: Tuple[LengthDimension, LengthDimension],
                   dst_size: Tuple[LengthDimension, LengthDimension]) -> Tuple[LengthDimension, LengthDimension]:
    """Returns the x, y scaling factors to be applied to src to fit within dst for the given scaling.
    :return: scaling factors for (x, y)
    """
    # handle X transform
    # if scaling in [Scaling.NONE, Scaling.FIT]:
