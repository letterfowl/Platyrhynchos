from sys import platform
from tempfile import NamedTemporaryFile

from dynaconf import Dynaconf


def load_settings_from_string(settings_text: str):
    """Load settings from a string. Useful for testing."""
    temp_settings = Dynaconf()
    with NamedTemporaryFile("w", suffix=".toml") as f:
        f.write(settings_text)
        f.flush()
        temp_settings.load_file(f.name)  # type: ignore
    return temp_settings


if platform == "emscripten":
    # Running in the browser, so we can't load settings from a file.

    # pylint: disable=import-error
    from _stuff import settings_text

    settings = load_settings_from_string(settings_text)["DEFAULT"]
    assert hasattr(settings, "debug"), "settings.debug not found"
else:
    settings = Dynaconf(settings_files=["settings.toml", ".secrets.toml"], environments=True)
