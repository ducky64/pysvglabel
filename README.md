# pysvglabel

Label generator with SVG templates supporting embedded Python code and CSV data

| Template | Output |
|:---:|:---:|
| ![Design Template](docs/design_screws_40x10mm_simple.png) <br/> [source SVG](examples/screws_40x10mm_simple.svg) <br/> with [supporting code](examples/screws.py) | ![Generated Labels](docs/output_screws_simple.png) <br/> from [data CSV](examples/screws.csv) |

## Usage

`python pysvglabel <template.svg> <data.csv>`

Label sheet data is embedded in the .svg file. All text in the .svg file is treated as Python f-strings, and the contents of the row (where the column name is a legal Python variable name) are made available. Specially formatted commands (see [Template Reference](#template-reference)) that call Python functions (such as generating barcodes) can also be written into the template.

**Security notes**: running the labelmaker can execute arbitrary Python code embedded in the template SVG and supporting scripts.
There should be no issues if you're designing your own template from scratch.
Treat templates from the internet as you might treat a document with macros - make sure you trust it before running it.
Not all embedded Python code may be visible graphical elements.

### Windows Label Printing

Additional packages are needed to use the label printer functionality on Windows.

`pip install pywin32`

Inkscape also needs to on your system PATH.

## Template Reference

TBD

## Developing

This project uses optional static typing annotations.
You can run mypy using:

```
mypy .
```

If using IntelliJ, you can use the [Mypy plugin](https://plugins.jetbrains.com/plugin/13348-mypy-official-).
