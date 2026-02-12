# this example uses the template engine with pysvglabel as a dependency

from pysvglabel import SvgTemplate
import xml.etree.ElementTree as ET

template = SvgTemplate("../tests/simple_1.75x0.5.svg")
# create the blank sheet
sheet = template.create_sheet()
# instantiate a page of labels and append to the sheet, with values specified as a list of dicts, one per label
sheet.append(
    template.apply_page(
        [
            {"id": "0", "barcode": "B00", "description": "zero", "spaced thing": "a"},
            {"id": "1", "barcode": "B01", "description": "one", "spaced thing": "b"},
        ]
    )
)

# ... which can be written out
with open("example_api.svg", "wb") as svgfile:
    svgfile.write(ET.tostring(sheet, "utf-8"))
