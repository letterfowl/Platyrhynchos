from contextlib import suppress
from os import remove
from os.path import isfile
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper
from typing import Optional

import duckdb
import requests
from tqdm_loggable.auto import tqdm

from ..commons.alphabit import Alphabit
from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..commons.settings import settings
from ..commons.utils import app_dir

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
    async def wrapper(*args, **kwargs):
        return [i[0] for i in await func(*args, **kwargs)]

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
    """Download `file` from S3. Requires ENV variables to be set."""
    logger.info("Downloading database")
    assert settings.s3.region and settings.s3.endpoint and settings.s3.bucket, "S3 settings not set"
    assert settings.s3_key_id and settings.s3_key_secret, "S3 credentials not set"
    s3_client = boto3.client(
        "s3",
        region_name=settings.s3.region,
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3_key_id,
        aws_secret_access_key=settings.s3_key_secret,
    )
    size = s3_client.head_object(Bucket=settings.s3.bucket, Key=file).get("ContentLength")
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
async def get_regex_w_alphabit(regex: str, alphabit: str, previous: str, word_amount: int = 20):
    if previous is None or not previous:
        previous_formatted = ["'A'"]
    else:
        previous_formatted = [f"'{i}'" for i in previous.split(",")]
    return cursor_execute(
        f"select distinct answer from clues where bit_count('{alphabit}'::BIT | alphabit)=length(alphabit) and regexp_matches(answer, '{regex}') and length(answer) > 1 and length(answer) > 1 and answer not in ({','.join(previous_formatted)}) order by random() limit {word_amount}"
    )


@convert_result_to_list
async def get_regex(regex: str, previous: str, word_amount: int = 20):
    if previous is None or not previous:
        previous_formatted = ["'A'"]
    else:
        previous_formatted = [f"'{i}'" for i in previous.split(",")]
    return cursor_execute(
        f"select distinct answer from clues where regexp_matches(answer, '{regex}') and length(answer) > 1 and answer not in ({','.join(previous_formatted)}) order by random() limit {word_amount}"
    )


@convert_result_to_list
async def get_random(max_size: int):
    return cursor_execute(
        f"select answer from clues where length(answer) > 1 and length(answer) < {max_size} order by random() limit 1"
    )
