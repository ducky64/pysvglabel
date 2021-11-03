import xml.etree.ElementTree as ET
from typing import Any, Dict


class SvgTemplate:
  def __init__(self, file: str):
    raise NotImplementedError

  def create_sheet(self) -> Any:  # TODO proper ETree type
    raise NotImplementedError

  def apply(self, row: Dict[str, str]) -> Any:  # TODO proper ETree type
    raise NotImplementedError
