from contextlib import suppress
from os import remove
from os.path import isfile
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

import duckdb
import requests
from tqdm_loggable.auto import tqdm

from ..commons.alphabit import Alphabit
from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..commons.utils import app_dir
from ..commons.settings import settings

try:
    import boto3
except ImportError:
    boto3 = None

_db_path = app_dir("user_cache_dir", "words.db")

def cursor_execute(sql, **kwargs):
    cursor = duckdb.connect(database=_db_path).cursor()
    res = cursor.execute(sql, kwargs).fetchall() if kwargs else cursor.execute(sql).fetchall()
    cursor.close()
    return res


def convert_result_to_list(func):
    def wrapper(*args, **kwargs):
        return [i[0] for i in func(*args, **kwargs)]

    return wrapper


def download_db(file):
    try:
        cursor_execute("SELECT answer, alphabit FROM clues LIMIT 1")
    except duckdb.CatalogException:
        if boto3 is None:
            log_mess = f"Database in {_db_path} exists, but does not have a valid clues table. Please run the GetGerghoWords pipeline with `--duckdb_path={_db_path}` to fix this."
            logger.error(log_mess)
            raise DatabaseException(log_mess)
        else:
            with suppress(FileNotFoundError):
                remove(_db_path)
            _get_from_s3(file)
    else:
        logger.info("Database found and checked")
        return


def _get_from_s3(file):
    logger.info("Downloading database")
    s3_client = boto3.client(
        "s3",
        region_name=settings.s3.region,
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3_key_id,
        aws_secret_access_key=settings.s3_key_secret,
    )
    size = s3_client.head_object(Bucket=settings.s3.bucket, Key=file).get(
        "ContentLength"
    )
    with tqdm(
        total=size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        s3_client.download_file(
            Key=file,
            Bucket=settings.s3.bucket,
            Filename=_db_path,
            Callback=pbar.update,
        )
    logger.info("Database downloaded")


@convert_result_to_list
def get_regex_w_alphabit(regex: str, alphabit: str):
    return cursor_execute(
        f"select answer from clues where bit_count({alphabit} | alphabit)=length(alphabit) and regexp_matches(answer, '{regex}')"
    )


@convert_result_to_list
def get_regex(regex: str):
    return cursor_execute(
        f"select answer from clues where regexp_matches(answer, '{regex}')"
    )


@convert_result_to_list
def get_random():
    return cursor_execute("select answer from clues limit 1")
