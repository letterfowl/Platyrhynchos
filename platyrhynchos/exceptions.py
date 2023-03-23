
class CrosswordException(Exception):
    pass

class TooLargeException(CrosswordException):
    pass

class UninsertableException(CrosswordException):
    pass

class PartNotFoundException(UninsertableException):
    pass

class DownloadSQLiteRegexException(Exception):
    def __init__(self, *args: object) -> None:
        logger.critical("Please download SQLite Regex from https://github.com/asg017/sqlite-regex/releases/latest and save it as `regex-ext` in cwd")
        super().__init__(*args)