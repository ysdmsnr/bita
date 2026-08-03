from __future__ import annotations

from bita.core import EnumField, MultiLangField
from bita.vocabulary import Motivation


class Annotation:
    def __init__(
        self,
        motivation: Motivation | str,
        *,
        x: int | None = None,
        y: int | None = None,
        w: int | None = None,
        h: int | None = None,
    ) -> None:
        self.motivation = EnumField(self, Motivation)
        self.motivation(motivation)
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.text_ = {}
        self.text = MultiLangField(self, "text_")

    @property
    def language(self) -> str:
        if self.text_:
            return list(self.text_.keys())[-1]
        return ""

    @property
    def value(self) -> str:
        return self.text_.get(self.language, "")
