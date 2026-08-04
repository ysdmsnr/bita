from __future__ import annotations

from typing import TYPE_CHECKING

from bita.vocabulary.version import V2, V3

if TYPE_CHECKING:
    from datetime import date

    from bita import Image, Profile


class Builder:
    def __init__(self, profile: Profile) -> None:
        self.profile = profile

    def base_uri(self, identifier: str) -> str:
        base_uri = self.profile.presentation_base_uri.removesuffix("/")
        return f"{base_uri}/{identifier}"

    def presentation_id(self, identifier: str) -> str:
        return f"{self.base_uri(identifier)}/manifest.json"

    def sequence_id(self, identifier: str, index: int = 1) -> str:
        return f"{self.base_uri(identifier)}/sequence/{index}"

    def canvas_id(self, identifier: str, index: int) -> str:
        return f"{self.base_uri(identifier)}/canvas/{index}"

    def range_id(self, identifier: str, index: int) -> str:
        return f"{self.base_uri(identifier)}/range/{index}"

    def __image_id(self, image: Image) -> str:
        base_uri = self.profile.image_base_uri.removesuffix("/")
        return f"{base_uri}/{image.identifier}"

    def image_id(self, image: Image) -> str:
        base_uri = self.__image_id(image)
        if self.profile.image_api_version == V2:
            return f"{base_uri}/full/full/0/default.jpg"
        if self.profile.image_api_version == V3:
            return f"{base_uri}/full/max/0/default.jpg"
        return ""

    def search_id(self, identifier: str) -> str:
        base_uri = self.profile.search_base_uri.removesuffix("/")
        return f"{base_uri}/{identifier}/"

    def image_service(self, image: Image) -> dict:
        lv = self.profile.image_api_level
        id_ = self.__image_id(image)
        if self.profile.image_api_version == V2:
            return {
                "@context": f"http://iiif.io/api/image/{V2}/context.json",
                "@id": id_,
                "profile": f"http://iiif.io/api/image/{V2}/level{lv}.json",
            }
        if self.profile.image_api_version == V3:
            return {
                "id": id_,
                "profile": f"level{lv}",
                "type": f"ImageService{V3}",
            }
        return {}

    def search_service(self, version: int, identifier: str) -> dict:
        v = self.profile.search_api_version
        id_ = self.search_id(identifier)
        if version == V2:
            return {
                "@context": f"http://iiif.io/api/search/{v}/context.json",
                "@id": id_,
                "profile": f"http://iiif.io/api/search/{v}/search",
            }
        if version == V3:
            return {
                "id": id_,
                "profile": f"http://iiif.io/api/search/{v}/search",
                "type": f"SearchService{v}",
            }
        return {}

    def format_nav_date(self, nav_date: date) -> str:
        return f"{nav_date.isoformat()}T00:00:00Z"
