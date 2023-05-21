from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

import duckdb
import requests
from tqdm_loggable.auto import tqdm

from ..commons.utils import app_dir
from ..commons.logger import logger

_db_path = app_dir("user_cache_dir", "en_simple.db")
_connection = duckdb.connect(database=_db_path)

def cursor_execute(sql, **kwargs):
    cursor = _connection.cursor()
    return cursor.execute(sql, kwargs)

def download_db_file(url: str):
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
