from pathlib import Path
from typing import Any

from fluent.runtime import FluentBundle, FluentResource
from fluent.runtime.types import FluentNone


class Translator:
    def __init__(self, bundle: FluentBundle, locale: str) -> None:
        self._bundle = bundle
        self.locale = locale

    def __call__(self, key: str, **kwargs: Any) -> str:
        message = self._bundle.get_message(key)
        value = message.value if message else None
        if value is None:
            return key
        rendered, _ = self._bundle.format_pattern(value, kwargs or None)
        if isinstance(rendered, FluentNone):
            return key
        return rendered


class I18n:
    def __init__(self, locales_dir: Path, default_locale: str = "ru") -> None:
        self.default_locale = default_locale
        self._locales_dir = locales_dir
        self._translators: dict[str, Translator] = {}
        self._discover()

    def _discover(self) -> None:
        for locale_path in sorted(p for p in self._locales_dir.iterdir() if p.is_dir()):
            locale = locale_path.name
            bundle = FluentBundle([locale], use_isolating=False)
            for ftl_file in sorted(locale_path.glob("*.ftl")):
                bundle.add_resource(FluentResource(ftl_file.read_text(encoding="utf-8")))
            self._translators[locale] = Translator(bundle, locale)

    @property
    def available(self) -> list[str]:
        return sorted(self._translators.keys())

    def get(self, locale: str | None) -> Translator:
        if locale and locale in self._translators:
            return self._translators[locale]
        return self._translators[self.default_locale]
