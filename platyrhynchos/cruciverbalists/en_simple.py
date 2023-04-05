from os import remove as remove_file
from os.path import isfile
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile

import duckdb
import requests
from tqdm_loggable.auto import tqdm

from ..commons.alphabit import MAX_ALPHABIT, to_alphabit
from ..commons.logger import logger
from ..commons.utils import app_dir
from ..crossword.colrow import ColRow
from .base import Cruciverbalist

URL = "https://cryptics.georgeho.org/data/clues.csv?_stream=on&_size=max"

def prepare_database():
    # while True:
    db_path = app_dir("user_cache_dir", "en_simple.db")
    is_fresh = not isfile(db_path)
    connection = duckdb.connect(database=db_path)
    cursor = connection.cursor()
    if is_fresh:
        download_db(cursor)
    return connection, cursor


def download_db(cursor):
    logger.info("Database image not found, downloading")
    head = requests.get(URL, stream=True)
    total_size = (
        int(head.headers.get('content-length', 0)) if head.ok else 200_000_000
    )
    with tqdm.wrapattr(NamedTemporaryFile("wb", suffix='.csv'), "write", total=total_size) as fd:
        fd: _TemporaryFileWrapper
        with requests.get(URL, stream=True) as r:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        fd.flush()
        logger.info("Finished download, converting")
        cursor.execute(f"CREATE TABLE clues AS SELECT * FROM '{fd.name}';")
    logger.info("Finished converting, opening the database")

    #     logger.info("Generating the alpha-bit filter")
    #     cursor.execute('ALTER TABLE clues ADD alphabit BLOB;')
    #     cursor.execute("UPDATE clues SET alphabit=to_alphabit(answer) where answer is not null;")
    #     connection.commit()

    logger.info("Finished preparing the database")

class EnglishSimpleCruciverbalist(Cruciverbalist):
    STATEMENTS = {
        "get_by_regex": f"""
        select answer from clues where answer IS NOT NULL and regexp_matches(answer, '%s')
        """,
        "get_random": """
        select answer from clues limit 1
        """
    }

    def eval_colrow(self, colrow: ColRow) -> int:
        return -len(list(colrow.cross_words()))

    def select_by_regex(self, regexes: list[str]) -> list[str] | None:
        _, cursor = prepare_database()
        for i in [i.upper() for i in regexes]:
            cursor.execute(self.STATEMENTS["get_by_regex"] % (i))
            if found := [j[0] for j in cursor.fetchall()]:
                return found

    def eval_word(self, word: str, colrow: ColRow) -> int:
        return len(word)

    def start_word(self) -> str:
        _, cursor = prepare_database()
        v = cursor.sql(self.STATEMENTS['get_random']).fetchone()
        return v[0]
