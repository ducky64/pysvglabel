from string import digits

# Abbreviations from
# https://monsterbolts.com/pages/abbreviations
# https://www.boltdepot.com/fastener-information/Abbreviations.aspx

def drive_svg(name: str) -> str:
  """Returns the SVG name for a given drive specification"""
  drive_type = name.rstrip(digits)
  return {
    "PH": "external/screws/phillips.svg",
    "SL": "external/screws/slot.svg",
    "T": "external/screws/torx.svg",
    "TS": "external/screws/torx-tamperproof.svg",
    "SQ": "external/screws/robertson.svg",
    "H": "external/screws/hex.svg",
  }[drive_type]

def head_svg(name: str) -> str:
  """Returns the SVG name for a given head geometry"""
  return "external/screws/torx.svg"
