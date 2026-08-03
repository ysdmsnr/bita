from __future__ import annotations

from typing import TYPE_CHECKING

from bita.core import MultiLangField

if TYPE_CHECKING:
    from bita import Canvas


class Image:
    def __init__(
        self,
        identifier: str,
        *,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        self.canvas: Canvas | None = None
        self.identifier = identifier
        self.width = width
        self.height = height

        self.x: int | None = None
        self.y: int | None = None

        self.label_ = {}
        self.label = MultiLangField(self, "label_")
