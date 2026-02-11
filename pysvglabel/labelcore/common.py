class BadTemplateException(Exception):
  """Base class for all template errors."""
  pass


SVG_NAMESPACE = '{http://www.w3.org/2000/svg}'
SODIPODI_NAMESPACE = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}'
INKSCAPE_NAMESPACE = '{http://www.inkscape.org/namespaces/inkscape}'
NAMESPACES = {
  'svg': 'http://www.w3.org/2000/svg',
  'inkscape': 'http://www.w3.org/2000/svg',
}


SVG_GRAPHICS_TAGS = [
  f'{SVG_NAMESPACE}circle',
  f'{SVG_NAMESPACE}ellipse',
  f'{SVG_NAMESPACE}image',
  f'{SVG_NAMESPACE}line',
  f'{SVG_NAMESPACE}mesh',
  f'{SVG_NAMESPACE}path',
  f'{SVG_NAMESPACE}polygon',
  f'{SVG_NAMESPACE}polyline',
  f'{SVG_NAMESPACE}rect',
  f'{SVG_NAMESPACE}text',
  f'{SVG_NAMESPACE}use',
  f'{SVG_NAMESPACE}g'
]
