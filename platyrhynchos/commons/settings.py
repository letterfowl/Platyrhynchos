from sys import platform
from tempfile import NamedTemporaryFile

from dynaconf import Dynaconf

if platform == "emscripten":
    from _stuff import settings_text

    settings = Dynaconf()
    with NamedTemporaryFile("w", suffix=".toml") as f:
        f.write(settings_text)
        f.flush()
        settings.load_file(f.name)  # type: ignore
        settings = settings["DEFAULT"]
    assert hasattr(settings, "debug"), "settings.debug not found"
else:
    settings = Dynaconf(settings_files=["settings.toml", ".secrets.toml"], environments=True)
