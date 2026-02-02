from collections.abc import Generator
from pathlib import Path
from textwrap import dedent
from typing import Any
from unittest.mock import MagicMock, patch

import _pytest.capture
import pytest

from subt.main import main

FIXTURES_PATH = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _clean_generated_file() -> Generator[Any, Any, Any]:
    yield

    for srt_file in Path.cwd().glob("*.translated.srt"):
        srt_file.unlink()


def test_help(capsys: _pytest.capture.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.args == (2,)

    captured = capsys.readouterr()

    assert not captured.out
    assert (
        captured.err
        == dedent(
            """
    usage: subt [-h] [-S SERVICE] [-s LANG] [-d LANG] [-V] sub_file
    subt: error: the following arguments are required: sub_file
    """,
        ).lstrip()
    )


def test_version(capsys: _pytest.capture.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as e:
        main(["-V"])
    assert e.value.args == (0,)

    captured = capsys.readouterr()

    assert captured.out.startswith("subt ")
    assert not captured.err


def test_translate(capsys: _pytest.capture.CaptureFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock translation mapping
    translations = {
        "Alright, so here we are, one of the elephants.": "さて、ここにゾウがいます。",
        "The cool thing about these guys is that they have really, really, really long trunks.": "この人たちのすごいところは、本当に、本当に、本当に長いトランクスを持っていることです。",
        "And that's cool.": "そしてそれはクールです。",
        "And that's pretty much all there is to say.": "そして、言いたいことはこれでほぼすべてです。",
    }

    # Create a mock translator
    mock_result = MagicMock()
    
    def mock_translate(text: str, dest: str, source: str = "auto") -> MagicMock:
        mock_result.result = translations.get(text, text)
        return mock_result

    mock_translator_instance = MagicMock()
    mock_translator_instance.translate = mock_translate
    
    # Create a mock translator class that returns our instance
    mock_translator_class = MagicMock(return_value=mock_translator_instance)

    # Use monkeypatch to replace GoogleTranslate in the __TRANSLATORS dictionary
    import subt.main
    translators_copy = subt.main.__TRANSLATORS.copy()
    translators_copy["google"] = mock_translator_class
    monkeypatch.setattr("subt.main.__TRANSLATORS", translators_copy)
    
    main([str(FIXTURES_PATH / "zoo.srt"), "-S", "google", "-d", "ja"])

    captured = capsys.readouterr()

    assert captured.out == "Saved: './zoo.translated.srt'\n"
    with (
        Path("zoo.translated.srt").open("r") as generated_file,
        (FIXTURES_PATH / "zoo.translated.srt").open("r") as expected_file,
    ):
        assert generated_file.read() == expected_file.read()
