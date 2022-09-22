# Core classes, not intended to be user-facing
from .SvgTemplate import SvgTemplate, filter_text_elts, filter_text_inner_elts
from .InkscapeSubprocess import InkscapeSubprocess

from .common import SVG_NAMESPACE, INKSCAPE_NAMESPACE, SODIPODI_NAMESPACE, NAMESPACES, BadTemplateException
from .GroupReplacer import GroupReplacer, RectGroupReplacer
