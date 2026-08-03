from __future__ import annotations

from typing import TYPE_CHECKING

from bita.core.multi_lang_field import MultiLangField

if TYPE_CHECKING:
    from bita.model.annotation import Annotation
    from bita.model.image import Image


class Canvas:
    def __init__(self, *, height: int, width: int) -> None:
        self.height = height
        self.width = width

        self.id_: str | None = None

        self.label_ = {}
        self.label = MultiLangField(self, "label_")

        self.images: list[Image] = []
        self.annotations: list[Annotation] = []

    def image(self, image: Image, *, x: int | None = None, y: int | None = None) -> Canvas:
        if image.height is None:
            image.height = self.height
        if image.width is None:
            image.width = self.width
        if image.x is None:
            image.x = x
        if image.y is None:
            image.y = y
        image.canvas = self
        self.images.append(image)
        return self

    def annotation(
        self,
        *annotation: Annotation,
    ) -> Canvas:
        self.annotations.extend(annotation)
        return self

    def has_annotation(self) -> bool:
        return bool(self.annotations)
