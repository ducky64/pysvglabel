from typing import List, Optional
import xml.etree.ElementTree as ET

from labelcore.GroupReplacer import RectGroupReplacer
from labelcore.common import SVG_NAMESPACE
from .units import LengthDimension, mm
from .Align import Align


class QrCode(RectGroupReplacer):
  """
  Adds a QR code where this rectangle-area-group is.
  The pixel size is a parameter.
  This requires the qrcode library (https://pypi.org/project/qrcode/)
    pip install qrcode
  """
  def __init__(self, data: str, size: LengthDimension, align: Align = Align.CENTER, fill: str = '#000000',
               border: Optional[int] = None, error_correction: Optional['int'] = None):
    """
    :param data: data of the barcode
    :param size: width of a box
    :param fill: fill color of the bars
    """
    assert isinstance(data, str) and isinstance(size, LengthDimension)
    self.data = data
    self.size = size
    self.align = align
    self.fill = fill
    self.border = border
    self.error_correction = error_correction

  def process_rect(self, rect: ET.Element) -> List[ET.Element]:
    import qrcode.image.svg  # type: ignore

    kwargs = {}
    if self.border is not None:
      kwargs['border'] = self.border
    if self.error_correction is not None:
      kwargs['error_correction'] = self.error_correction

    qr = qrcode.QRCode(
      version=None,
      box_size=10,  # the code says =1mm, but actually =1px
      image_factory=qrcode.image.svg.SvgPathImage,
      **kwargs
    )
    qr.add_data(self.data)
    qr.make(fit=True)

    # qrcode internally is dynamically lxml or xml, so serialize and deserialize to standardize
    svg_str = qr.make_image().to_string(encoding='unicode')
    path = ET.fromstring(svg_str)[0]  # type: ET.Element

    x = LengthDimension.from_str(rect.attrib['x'])
    y = LengthDimension.from_str(rect.attrib['y'])
    width = LengthDimension.from_str(rect.attrib['width'])
    height = LengthDimension.from_str(rect.attrib['height'])
    data_height = data_width = len(qr.get_matrix())
    align_x, align_y = Align.to_transform(self.align, (self.size * data_width, self.size * data_height),
                                          (width, height))
    assert self.size * data_width <= width and self.size * data_height < height, \
      f"{self.__class__.__name__} {self.data} with {data_width}x{data_height} matrix overflowed"

    assert 'transform' not in path.attrib  # make sure it doesn't exist before it gets overwritten
    path.attrib['transform'] = f'translate({(x + align_x).to_str()} {(y + align_y).to_str()}) scale({self.size.to_px()})'

    assert 'fill' in path.attrib
    path.attrib['fill'] = self.fill

    return [path]
