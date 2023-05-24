from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

import duckdb
import requests
from tqdm_loggable.auto import tqdm

from ..commons.alphabit import Alphabit
from ..commons.logger import logger
from ..commons.utils import app_dir

_db_path = app_dir("user_cache_dir", "en_simple.db")
_connection = duckdb.connect(database=_db_path)


def cursor_execute(sql, **kwargs):
    cursor = _connection.cursor()
    return cursor.execute(sql, kwargs)


def download_db(url: str):
    logger.info("Downloading the database")
    head = requests.head(url, timeout=60)
    total_size = int(head.headers.get("content-length", -1)) if head.ok else -1
    with tqdm.wrapattr(NamedTemporaryFile("wb", suffix=".csv"), "write", total=total_size) as temp_file:
        temp_file: _TemporaryFileWrapper
        with requests.get(url, stream=True, timeout=60) as csv_stream:
            for chunk in csv_stream.iter_content(chunk_size=128):
                temp_file.write(chunk)
        temp_file.flush()
        logger.info("Finished download, converting")
        cursor_execute(f"CREATE TABLE clues AS SELECT * FROM '{temp_file.name}';")

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
            file=alphabit_cache.name,
        )
    logger.info("Finished preparing the database")


def get_regex_w_alphabit(regex: str, alphabit: int):
    return cursor_execute(
        f"select answer from clues where bit_count({alphabit} | alphabit)=length(alphabit) and regexp_matches(answer, '{regex}')"
    ).fetch_all()


def get_regex(regex: str):
    return cursor_execute(f"select answer from clues where regexp_matches(answer, '{regex}')").fetch_all()


def get_random():
    return cursor_execute("select answer from clues limit 1").fetch_one()
