import subprocess


class InkscapeSubprocess:
  """
  A class for an Inkscape subprocess to convert SVG to PDF.

  We use Inkscape instead of ReportLab / svglib because svglib doesn't seem to render some features correctly,
  like flowRegion.
  Inkscape in shell mode is also pretty responsive.
  """
  def __init__(self) -> None:
    self.process = subprocess.Popen(["inkscape", "--shell"], stdin=subprocess.PIPE)
    # don't block for Inkscape to start up, just start sending commands

  def convert(self, filename_in: str, filename_out: str) -> None:
    # IMPORTANT - this does not check for conversion completion
    assert self.process.stdin
    self.process.stdin.write(str.encode(f'file-open:{filename_in};export-filename:{filename_out};export-do;\r\n'))
    self.process.stdin.flush()

  def close(self) -> None:
    assert self.process.stdin
    self.process.stdin.write(b'quit\r\n')
    self.process.stdin.flush()
    self.process.communicate()  # Inkscape may still be converting
