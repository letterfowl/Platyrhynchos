from ..commons.settings import settings
from .old_base import CruciverbalistOldBase

if settings.components["cruciverbalist"] == "en_simple":
    from .en_simple import EnglishSimpleCruciverbalist as Cruciverbalist
