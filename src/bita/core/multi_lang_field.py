from __future__ import annotations

from bita.vocabulary import DEFAULT_LANGUAGE


class MultiLangField:
    def __init__(self, model, name: str) -> None:
        self.model = model
        self.name = name

    def add(self, lang: str, value: str) -> None:
        field = getattr(self.model, self.name)
        field[lang] = value

    def value(self) -> dict:
        if self.data:
            return {k: [v] for k, v in self.data.items()}
        return {}

    def default_lang_value(self) -> str:
        return self.data.get(DEFAULT_LANGUAGE, "")

    @property
    def data(self) -> dict:
        if hasattr(self.model, self.name) and getattr(self.model, self.name):
            return getattr(self.model, self.name)
        return {}

    def __call__(self, *args):
        if len(args) == 1:
            lang = DEFAULT_LANGUAGE
            value = args[0]
        elif len(args) == 2:  # noqa: PLR2004
            lang, value = args
        else:
            raise TypeError("MultiLangField takes 1 or 2 arguments")
        self.add(lang, value)
        return self.model

    def __getattr__(self, lang: str):
        def wrapper(value: str):
            self.add(lang, value)
            return self.model

        return wrapper
