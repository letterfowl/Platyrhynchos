# trunk-ignore(flake8/F401)
from ..commons.settings import settings
from .base import Cruciverbalist

if settings.components["cruciverbalist"] == "en_simple":
    from .en_simple import EnglishSimpleCruciverbalist
