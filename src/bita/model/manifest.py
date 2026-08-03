from __future__ import annotations

import json
from typing import TYPE_CHECKING

from bita.core import EnumField, MultiLangField
from bita.serializer.serializer import Serializer, VersionError
from bita.vocabulary import Behavior, ViewingDirection
from bita.vocabulary.version import V2

if TYPE_CHECKING:
    from datetime import date

    from bita import Canvas, Metadata, Profile, Provider, Range


class Manifest:
    def __init__(self, identifier: str) -> None:
        self.identifier_ = identifier

        self.metadata_ = []
        self.canvas_ = []
        self.structure_ = []

        self.label_ = {}
        self.label = MultiLangField(self, "label_")
        self.description_ = {}
        self.description = MultiLangField(self, "description_")
        self.attribution_ = {}
        self.attribution = MultiLangField(self, "attribution_")

        self.viewing_direction = EnumField(self, ViewingDirection)
        self.behavior = EnumField(self, Behavior)

    def license(self, license_: str) -> Manifest:
        self.license_ = license_
        return self

    def terms(self, terms: str) -> Manifest:
        self.terms_ = terms
        return self

    def provider(self, provider: Provider) -> Manifest:
        self.provider_ = provider
        return self

    def nav_date(self, nav_date: date) -> Manifest:
        self.nav_date_ = nav_date
        return self

    def metadata(self, *metadata: Metadata) -> Manifest:
        self.metadata_.extend(metadata)
        return self

    def canvas(self, *canvas: Canvas) -> Manifest:
        self.canvas_.extend(canvas)
        return self

    def structure(self, *range_: Range) -> Manifest:
        self.structure_.extend(range_)
        return self

    def to_dict(self, *, version: int, profile: Profile) -> dict:
        return Serializer(version, profile).serialize(self)

    def to_json(self, *, version: int, profile: Profile) -> str:
        return json.dumps(Serializer(version, profile).serialize(self), sort_keys=True)

    def create_annotation_list(self, *, version: int, profile: Profile) -> dict:
        if version != V2:
            raise VersionError
        return Serializer(version, profile).create_annotation_list(self)
