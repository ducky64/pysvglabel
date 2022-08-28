# Core classes, not intended to be user-facing
from .SvgTemplate import SvgTemplate
from .InkscapeSubprocess import InkscapeSubprocess

from .common import SVG_NAMESPACE, NAMESPACES, BadTemplateException
from .GroupReplacer import GroupReplacer, RectGroupReplacer
