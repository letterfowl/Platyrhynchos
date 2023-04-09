from os.path import isfile
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile

import duckdb
import requests
from tqdm_loggable.auto import tqdm

from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..commons.utils import app_dir
from ..commons.alphabit import Alphabit
from ..crossword.colrow import ColRow
from .base import Cruciverbalist


URL = "https://cryptics.georgeho.org/data/clues.csv?_stream=on&_size=max"
RUN_WITH_ALPHABIT = True


def prepare_database():
    db_path = app_dir("user_cache_dir", "en_simple.db")
    is_fresh = not isfile(db_path)
    connection = duckdb.connect(database=db_path)
    cursor = connection.cursor()
    if is_fresh:
        download_db(cursor)
    return connection, cursor


def download_db(cursor: duckdb.DuckDBPyConnection):
    logger.info("Database image not found, downloading")
    head = requests.get(URL, stream=True)
    total_size = (
        int(head.headers.get("content-length", 120_000_000)) if head.ok else 120_000_000
    )
    with tqdm.wrapattr(
        NamedTemporaryFile("wb", suffix=".csv"), "write", total=total_size
    ) as temp_file:
        temp_file: _TemporaryFileWrapper
        with requests.get(URL, stream=True) as csv_stream:
            for chunk in csv_stream.iter_content(chunk_size=128):
                temp_file.write(chunk)
        temp_file.flush()
        logger.info("Finished download, converting")
        cursor.execute(f"CREATE TABLE clues AS SELECT * FROM '{temp_file.name}';")
    logger.info("Finished converting, preprocessing")

    cursor.execute(
        """
        DELETE FROM clues WHERE answer IS NULL;
        ALTER TABLE clues ADD alphabit BIT
    """
    )
    answers = cursor.sql("SELECT rowid, answer FROM clues").fetchall()
    with NamedTemporaryFile("w", suffix=".csv") as alphabit_cache:
        alphabit_cache.writelines(
            tqdm(
                (f"{rowid},{Alphabit(answer).to_db()}\n" for rowid, answer in answers),
                total=len(answers),
            )
        )
        cursor.execute(
            """
        UPDATE clues
        SET alphabit = (
            SELECT alphabit
            FROM read_csv($file, columns={row:int, alphabit:bit}) as new
            WHERE clues.rowid = new.row
        );
        """,
            {"file": alphabit_cache.name},
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
        super().__init__()
        _, self.cursor = prepare_database()

    def _sql_regex(self, **kwargs):
        if RUN_WITH_ALPHABIT:
            self.cursor.execute(self.STATEMENTS["get_regex_w_alphabit"] % kwargs)
        else:
            self.cursor.execute(self.STATEMENTS["get_regex"] % kwargs)
        return found if (found := [j[0] for j in self.cursor.fetchall()]) else None

    def eval_colrow(self, colrow: ColRow) -> int:
        return -len(list(colrow.cross_words()))

    def select_by_regex(self, regexes: list[str]) -> list[str] | None:
        for i in [i.upper() for i in regexes]:
            if RUN_WITH_ALPHABIT:
                alp = Alphabit(i).to_query()
                if ret := self._sql_regex(regex=i, alphabit=alp):
                    return ret
            elif ret := self._sql_regex(regex=i):
                return ret

    def eval_word(self, word: str, colrow: ColRow) -> int:
        return len(word) + len(list(colrow.cross_words()))

    def start_word(self) -> str:
        v = self.cursor.sql(self.STATEMENTS["get_random"]).fetchone()
        if v is None:
            raise DatabaseException("Couldn't find any words.")
        return v[0]
