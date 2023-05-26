import os
from os.path import isfile
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
    return cursor.execute(sql, kwargs) if kwargs else cursor.execute(sql)


def convert_result_to_list(func):
    def wrapper(*args, **kwargs):
        return [i[0] for i in func(*args, **kwargs).fetchall()]

    return wrapper


def download_db(url: str):
    if not isfile(_db_path):
        log_mess = f"Database does not exist. Please run the GetGerghoWords pipeline with `--duckdb_path={_db_path}` to fix this."
        logger.error(log_mess)
        raise DatabaseError(log_mess)
    try:
        cursor_execute("SELECT answer, alphabit FROM clues LIMIT 1")
    except duckdb.CatalogException:
        log_mess = f"Database in {_db_path} exists, but does not have a valid clues table. Please run the GetGerghoWords pipeline with `--duckdb_path={_db_path}` to fix this."
        logger.error(log_mess)
        raise DatabaseError(log_mess)
    else:
        logger.info("Database found and checked")
        return


@convert_result_to_list
def get_regex_w_alphabit(regex: str, alphabit: str):
    return cursor_execute(
        f"select answer from clues where bit_count({alphabit} | alphabit)=length(alphabit) and regexp_matches(answer, '{regex}')"
    )


@convert_result_to_list
def get_regex(regex: str):
    return cursor_execute(f"select answer from clues where regexp_matches(answer, '{regex}')")


@convert_result_to_list
def get_random():
    return cursor_execute("select answer from clues limit 1")
