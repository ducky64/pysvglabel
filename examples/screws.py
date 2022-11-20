from string import digits

from labelfrontend.units import LengthDimension, mm


# Abbreviations from
# https://monsterbolts.com/pages/abbreviations
# https://www.boltdepot.com/fastener-information/Abbreviations.aspx


def drive_svg(name: str) -> str:
  """Returns the SVG name for a given drive specification"""
  drive_type = name.rstrip(digits + '.')
  return {
    "PH": "external/screws/phillips.svg",
    "SL": "external/screws/slot.svg",
    "T": "external/screws/torx.svg",
    "TS": "external/screws/torx-tamperproof.svg",
    "SQ": "external/screws/robertson.svg",
    "H": "external/screws/hex.svg",
    "HX": "external/screws/hex-external.svg",
  }.get(drive_type, None)

def head_svg(name: str) -> str:
  """Returns the SVG name for a given head geometry"""
  return {
    "PN": "screws/pan.svg",
    "BH": "screws/round.svg",  # button
    "CS": "screws/countersunk90.svg",
    "OV": "screws/countersunk-round.svg",
    "HX": "screws/hex.svg",
    "HXF": "screws/hex-flanged.svg",
    "SKT": "screws/socket.svg",
    "SetFlat": "screws/set-flat.svg",
    "SetCup": "screws/set-cup.svg",
    "SetCone": "screws/set-cone.svg",
    "SetDog": "screws/set-dog.svg",
  }.get(name, None)

def thread_dia(value: str) -> LengthDimension:
  if value.startswith("M"):
    return float(value[1:]) * mm
  else:
    raise ValueError(f"unknown thread {value}")

def to_dim(value: str) -> LengthDimension:
  if value.endswith("mm"):
    return float(value[:-2]) * mm
  else:
    raise ValueError(f"unknown dimension {value}")
