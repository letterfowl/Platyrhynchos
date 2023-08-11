"""All platyrhynchos exceptions"""


class CrosswordException(Exception):
    """Parent of other crossword-related exceptions"""

    pass


class TooLargeException(CrosswordException):
    """CrosswordImprovable became too large"""

    pass


class UninsertableException(CrosswordException):
    """Letter cannot be inserted, possibly due to overlapping"""

    pass


class PartNotFoundException(UninsertableException):
    """ColRow.pos_of_word couldn't localize the word"""

    pass


class DatabaseException(Exception):
    """Parent of db-related exceptions"""

    pass

class WordNotFoundError(CrosswordException):
    """Word not found in crossword"""

    pass