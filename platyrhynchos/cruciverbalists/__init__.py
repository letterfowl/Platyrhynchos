# trunk-ignore(flake8/F401)
from .base import Cruciverbalist
from ..commons.settings import settings

if settings.components['cruciverbalist'] == "en_simple":
    from .en_simple import EnglishSimpleCruciverbalist
