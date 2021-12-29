# pysvglabel

Label generator with SVG templates supporting embedded Python code and CSV data

## Usage

`python pysvglabel <template.svg> <data.csv>`

Label sheet data is embedded in the .svg file. All text in the .svg file is treated as Python f-strings, and the contents of the row (where the column name is a legal Python variable name) are made available. Additional 

**SECURITY WARNING**, if downloading templates off the internet: running the label generator on a template can execute arbitrary Python code in the template. Make sure you trust or examine templates you download!

A future version may sandbox templates by default, limiting what Python functions they can access.

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
mypy --disallow-untyped-defs .
```

If using IntelliJ, you can use the [Mypy plugin](https://plugins.jetbrains.com/plugin/13348-mypy-official-), adding `--disallow-untyped-defs` to the [configuration](https://github.com/dropbox/mypy-PyCharm-plugin#configuration).
