from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enum import StrEnum


class EnumField:
    def __init__(self, model, enum: type[StrEnum]) -> None:
        self.model = model
        self.enum = enum
        self.values = []
        self.value = ""

    def __call__(self, *args):
        value = args[0]
        self.validate_enum(value)
        return self.model

    def validate_enum(self, value: str):
        try:
            self.enum(value)
            self.value = str(value)
            self.values.append(self.value)
            self.values = list(set(self.values))
        except ValueError:
            raise ValueError(f"Invalid value '{value}' for {self.enum.__name__}")
