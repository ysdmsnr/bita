from __future__ import annotations

from typing import TYPE_CHECKING

from bita.core import MultiLangField

if TYPE_CHECKING:
    from bita import Canvas


class Range:
    def __init__(self, *members: Canvas | Range) -> None:
        self.label_ = {}
        self.label = MultiLangField(self, "label_")

        self.members_ = []
        self.members_.extend(members)
