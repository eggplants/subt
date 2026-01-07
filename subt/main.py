"""This script translates subtitles in a subtitle file using translation service.

Example:
subt example.srt -S google -s en -d fr
"""

from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path

import pysubs2
from translatepy import language  # type: ignore[import-untyped]
from translatepy.translators import (  # type: ignore[import-untyped]
    BingTranslate,
    DeeplTranslate,
    GoogleTranslate,
    LibreTranslate,
    MicrosoftTranslate,
    MyMemoryTranslate,
    ReversoTranslate,
    TranslateComTranslate,
    YandexTranslate,
)

__TRANSLATORS = {
    "google": GoogleTranslate,
    "yandex": YandexTranslate,
    "microsoft": MicrosoftTranslate,
    "reverso": ReversoTranslate,
    "bing": BingTranslate,
    "deepl": DeeplTranslate,
    "libre": LibreTranslate,
    "translate_com": TranslateComTranslate,
    "my_memory": MyMemoryTranslate,
}


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    """Custom formatter for argparse."""


def __get_services() -> tuple[str, ...]:
    return tuple(__TRANSLATORS)


def __get_languages() -> tuple[str, ...]:
    return tuple(str(lang["2"]) for lang in language.LANGUAGE_DATA.values() if "2" in lang)


def __parse_args(test_args: list[str] | None = None) -> argparse.Namespace:
    package_info = metadata.metadata("subt")
    parser = argparse.ArgumentParser(
        prog=package_info.get("Name"),
        description=package_info.get("Summary"),
        formatter_class=CustomFormatter,
    )
    parser.add_argument(
        "sub_file",
        type=str,
    )
    parser.add_argument(
        "-S",
        choices=__get_services(),
        dest="service",
        default="google",
        metavar="SERVICE",
        help="service to translate",
    )
    parser.add_argument(
        "-s",
        dest="source_language",
        choices=__get_languages(),
        default="auto",
        metavar="LANG",
        help="source language",
    )
    parser.add_argument(
        "-d",
        dest="destination_language",
        choices=__get_languages(),
        default="en",
        metavar="LANG",
        help="destination language",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{package_info.get('Name')} {package_info.get('Version')}",
    )
    if test_args:
        return parser.parse_args(test_args)
    return parser.parse_args()


def main(test_args: list[str] | None = None) -> None:
    args = __parse_args(test_args)
    translator = __TRANSLATORS[args.service]()

    sub_file_path = Path(args.sub_file)
    subs = pysubs2.load(str(sub_file_path), encoding="utf-8")
    for sub in subs:
        sub.text = translator.translate(
            sub.text,
            args.destination_language,
            args.source_language,
        ).result

    out_file_name = sub_file_path.with_suffix(f".translated.{subs.format}").name
    subs.save(out_file_name)

    print(f"Saved: './{out_file_name}'")


__all__ = tuple("main")

if __file__ == "__main__":
    main()
