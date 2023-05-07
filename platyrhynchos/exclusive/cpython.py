import duckdb
from ..commons.utils import app_dir

_db_path = app_dir("user_cache_dir", "en_simple.db")
_connection = duckdb.connect(database=_db_path)
def cursor_execute(sql, **kwargs):
    cursor = _connection.cursor()
    return cursor.execute(sql, kwargs)