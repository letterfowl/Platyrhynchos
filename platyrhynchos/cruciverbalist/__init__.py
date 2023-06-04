from ..commons.settings import settings
from .base import CruciverbalistBase

if settings.components["cruciverbalist"] == "en_simple":
    from .en_simple import EnglishSimpleCruciverbalist as Cruciverbalist
