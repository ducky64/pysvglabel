from typing import List
from abc import ABCMeta, abstractmethod

import xml.etree.ElementTree as ET

from .SvgTemplate import SvgTemplate
from .common import BadTemplateException, SVG_NAMESPACE


class GroupReplacer(metaclass=ABCMeta):
    """Abstract base class for group replacement in a template SVG:
    in the template, for a group with a text box, where the text begins with 🐍,
    the remaining text is interpreted as Python and returns an object of this class,
    which is when invoked on the group (minus the text box) to mutate it as needed.
    """

    @abstractmethod
    def process_group(self, elts: List[ET.Element]) -> List[ET.Element]:
        """Given the group contents (minus the textbox), returns the new group contents."""
        raise NotImplementedError


class RectGroupReplacer(GroupReplacer):
    """A GroupReplacer where the group only contains the textbox and a rect (eg, for area sizing)."""

    def process_group(self, elts: List[ET.Element]) -> List[ET.Element]:
        if len(elts) != 1 or elts[0].tag != f"{SVG_NAMESPACE}rect":
            group_tags = [elt.tag for elt in elts]
            raise BadTemplateException(
                f"{self.__class__.__name__}(RectGroupReplacer) expects single rect, got {group_tags}"
            )
        return self.process_rect(elts[0])

    @abstractmethod
    def process_rect(self, rect: ET.Element) -> List[ET.Element]:
        raise NotImplementedError
