from enum import Enum
from typing import Tuple

from .units import LengthDimension, px


class Scaling(Enum):
  NONE = 1,
  FIT = 2,  # fits to the smallest axis
  FIT_MAX = 3,  # fits to the largest axis

  @staticmethod
  def to_transform(scaling: 'Scaling', src_size: Tuple[LengthDimension, LengthDimension],
                   dst_size: Tuple[LengthDimension, LengthDimension]) -> Tuple[float, float]:
    """Returns the x, y scaling factors to be applied to src to fit within dst for the given scaling.
    :return: scaling factors for (x, y)
    """
    if scaling == Scaling.NONE:
      return 1.0, 1.0
    elif scaling == Scaling.FIT:
      width_scale = dst_size[0].to_px() / src_size[0].to_px()
      height_scale = dst_size[1].to_px() / src_size[1].to_px()
      scale = min(width_scale, height_scale)
      return scale, scale
    elif scaling == Scaling.FIT_MAX:
      width_scale = dst_size[0].to_px() / src_size[0].to_px()
      height_scale = dst_size[1].to_px() / src_size[1].to_px()
      scale = max(width_scale, height_scale)
      return scale, scale
    else:
      raise NotImplementedError
