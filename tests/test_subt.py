from pathlib import Path
from textwrap import dedent

import _pytest.capture
import pytest

from subt.main import main

FIXTURES_PATH = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _clean_generated_file() -> None:

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


def test_translate(capsys: _pytest.capture.CaptureFixture) -> None:
    main([str(FIXTURES_PATH / "zoo.srt"), "-S", "google", "-d", "ja"])

    captured = capsys.readouterr()

    assert captured.out == "Saved: './zoo.translated.srt'\n"
    with (
        Path("zoo.translated.srt").open("r") as generated_file,
        (FIXTURES_PATH / "zoo.translated.srt").open("r") as expected_file,
    ):
        assert generated_file.read() == expected_file.read()
