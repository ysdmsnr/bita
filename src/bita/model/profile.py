from __future__ import annotations


class Profile:
    def __init__(
        self,
        *,
        presentation_base_uri: str,
        image_base_url: str,
        image_api_version: int,
        image_api_level: int,
        search_base_url: str = "",
        search_api_version: int | None = None,
    ) -> None:
        if not presentation_base_uri:
            raise ValueError
        if not image_base_url:
            raise ValueError
        if not image_api_version:
            raise ValueError
        if image_api_version not in (1, 2, 3):
            raise ValueError
        if not image_api_level:
            raise ValueError
        if image_api_level not in (0, 1, 2):
            raise ValueError
        if search_api_version and search_api_version not in (1, 2):
            raise ValueError
        self.presentation_base_uri = presentation_base_uri
        self.image_base_url = image_base_url
        self.image_api_version = image_api_version
        self.image_api_level = image_api_level
        self.search_base_url = search_base_url
        self.search_api_version = search_api_version
