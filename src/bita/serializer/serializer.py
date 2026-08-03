from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bita import Profile

from bita.vocabulary.version import V2, V3

from .v2 import V2Builder
from .v3 import V3Builder


class VersionError(ValueError):
    def __init__(self):
        super().__init__("Unsupported version")


class Serializer:
    def __init__(self, version: int, profile: Profile):
        if version == V2:
            self.serialize = V2Builder(profile).serialize
            self.create_annotation_list = V2Builder(profile).create_annotation_list
        elif version == V3:
            self.serialize = V3Builder(profile).serialize
        else:
            raise VersionError
