from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

from tqdm_loggable.auto import tqdm

from ..commons.alphabit import Alphabit
from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..crossword.colrow import ColRow
from .base import Cruciverbalist
from ..exclusive import cursor_execute, download_db_file


URL = "https://cryptics.georgeho.org/data/clues.csv?_stream=on&_size=max"
RUN_WITH_ALPHABIT = True


def download_db():
    """Download and preprocess the database. Generates temporary files."""
    logger.info("Downloading the database")
    download_db_file(URL)
    logger.info("Finished downloading the database")

    # Preprocess the database
    cursor_execute(
        """
        DELETE FROM clues WHERE answer IS NULL;
        ALTER TABLE clues ADD alphabit BIT
    """
    )
    answers = cursor_execute("SELECT rowid, answer FROM clues").fetchall()
    with NamedTemporaryFile("w", suffix=".csv") as alphabit_cache:
        alphabit_cache.writelines(
            tqdm(
                (f"{rowid},{Alphabit(answer).to_db()}\n" for rowid, answer in answers),
                total=len(answers),
            )
        )
        cursor_execute(
            """
        UPDATE clues
        SET alphabit = (
            SELECT alphabit
            FROM read_csv($file, columns={row:int, alphabit:bit}) as new
            WHERE clues.rowid = new.row
        );
        """,
            file=alphabit_cache.name
        )

    logger.info("Finished preparing the database")


class EnglishSimpleCruciverbalist(Cruciverbalist):
    STATEMENTS = {
        "get_regex_w_alphabit": """
        select answer from clues where bit_count(%(alphabit)s | alphabit)=length(alphabit) and regexp_matches(answer, '%(regex)s')
        """,
        "get_regex": """
        select answer from clues where regexp_matches(answer, '%(regex)s')
        """,
        "get_random": """
        select answer from clues limit 1
        """,
    }

    def __init__(self) -> None:
        """Prepares the database"""
        download_db()
        super().__init__()

    def _sql_regex(self, **kwargs):
        """
        Queries the database for regex. Uses get_regex_w_alphabit or get_regex query.
        Keyword arguments are parsed to the query for string interpolation.
        """
        if RUN_WITH_ALPHABIT:
            found = cursor_execute(self.STATEMENTS["get_regex_w_alphabit"] % kwargs)
        else:
            found = cursor_execute(self.STATEMENTS["get_regex"] % kwargs)
        return found if (found := [j[0] for j in found.fetchall()]) else None

    def eval_colrow(self, colrow: ColRow) -> int:
        """
        Evaluates the ColRow as the next one to add a word to.
        Returns the number of words colliding with the colrow.
        """
        return -len(list(colrow.cross_words()))

    def select_by_regex(self, regexes: list[str]) -> list[str] | None:
        """
        Select compatible words using regex. It accepts a list of regular expressions and checks all one by one.
        """
        for i in [i.upper() for i in regexes]:
            if RUN_WITH_ALPHABIT:
                # Returns an alphabit query
                alp = Alphabit(i).to_query()
                if ret := self._sql_regex(regex=i, alphabit=alp):
                    return ret
            elif ret := self._sql_regex(regex=i):
                return ret
        return None

    def eval_word(self, word: str, colrow: ColRow) -> int:
        """Evaluate the word as an insertion into a ColRow."""
        return len(word) + len(list(colrow.cross_words()))

    def start_word(self) -> str:
        """Get a random word from the database. This is useful for testing the crossword."""
        found_words = cursor_execute(self.STATEMENTS["get_random"]).fetchone()
        # If there are any words in the database raise a DatabaseException.
        if found_words is None:
            raise DatabaseException("Couldn't find any words.")
        return found_words[0]
