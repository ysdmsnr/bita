from __future__ import annotations

from bita.core import MultiLangField


class Metadata:
    def __init__(self) -> None:
        self.label_ = {}
        self.label = MultiLangField(self, "label_")
        self.value_ = {}
        self.value = MultiLangField(self, "value_")

    @property
    def data(self) -> dict:
        return {"label": self.label_, "value": self.value_}
