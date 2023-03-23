from os.path import isfile
from os import remove as remove_file
import sqlite3 as sql
import sqlite_regex
import re

import requests
from tqdm_loggable.auto import tqdm

from ..logger import logger
from ..colrow import ColRow
from . import Cruciverbalist
from ..utils import app_dir

sql.enable_callback_tracebacks(True)

URL = "https://cryptics.georgeho.org/data.db"

def prepare_database():
    while True:
        db_path = app_dir("user_cache_dir", "georgeho.db")
        if not isfile(db_path):
            logger.info("Database image not found, downloading")
            with requests.get(URL, stream=True) as r:
                total_size = int(r.headers.get('content-length', 200_000_000))
                with tqdm.wrapattr(open(db_path, 'wb'), "write", total=total_size) as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
            logger.info("Done!")

        connection = sql.connect(db_path)
        connection.enable_load_extension(True)
        sqlite_regex.load(connection)
        cursor = connection.cursor()
        try:
            cursor.execute("select 1").fetchall()
        except sql.DatabaseError:
            logger.error("Database disk image is malformed, redownloading")
            remove_file(db_path)
            continue
        break
        
    return connection, cursor

DB_CONNECTION, DB_CURSOR = prepare_database()

class EnglishSimpleCruciverbalist(Cruciverbalist):
    STATEMENTS = {
        "get_by_regex": """
        select answer from clues inner join 
        (
            select rowid as row_answer, answer regexp '%s' as found from clues
            where answer is not null
        ) 
        on rowid=row_answer where found=1
        """
    }

    def eval_colrow(self, colrow: ColRow) -> int:
        return -len(list(colrow.cross_words()))

    def select_by_regex(self, regexes: list[str]) -> list[str] | None:
        for i in [i.upper() for i in regexes]:
            DB_CURSOR.execute(self.STATEMENTS["get_by_regex"] % i)
            if found := [j[0] for j in DB_CURSOR.fetchall()]:
                return found

    def eval_word(self, word: str, colrow: ColRow) -> int:
        return len(word)
