class CrosswordException(Exception):
    pass


class TooLargeException(CrosswordException):
    pass


class UninsertableException(CrosswordException):
    pass


class PartNotFoundException(UninsertableException):
    pass


class DatabaseException(Exception):
    pass
