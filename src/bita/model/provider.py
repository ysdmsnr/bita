from __future__ import annotations

from bita.core import MultiLangField


class Provider:
    def __init__(self) -> None:
        self.name_ = {}
        self.name = MultiLangField(self, "name_")

    def logo(self, logo: str) -> Provider:
        self.logo_ = logo
        return self

    def homepage(self, homepage: str) -> Provider:
        self.homepage_ = homepage
        return self
