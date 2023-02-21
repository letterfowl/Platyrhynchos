from abc import ABC, abstractmethod
from libs.crossword_improvable import CrosswordImprovable
from libs.utils import CruciverbalistDecision

class Cruciverbalist(ABC):

    @abstractmethod
    def __call__(self, crossword: CrosswordImprovable) -> CruciverbalistDecision:
        pass
    