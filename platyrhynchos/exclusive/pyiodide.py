from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from typing import Any, Optional
from duckdb_wasm import connector
from asyncio import get_event_loop
from pyodide.http import pyfetch, FetchResponse
from tqdm_loggable.auto import tqdm
from async_to_sync import function as async_to_sync

from ..commons.logger import logger

# https://pyodide.org/en/stable/usage/api/python-api/http.html#pyodide.http.pyfetch

def cursor_execute(sql, **kwargs): # type: ignore
    async def _execute():
        connection = await connector()
        return await connection.query(sql, kwargs)
    return async_to_sync(_execute)()

async def request(url: str, method: str = "GET", body: Optional[str] = None,
                  headers: Optional[dict[str, str]] = None, **fetch_kwargs: Any) -> FetchResponse:
    """
    Async request function. Pass in Method and make sure to await!
    Parameters:
        url: str = URL to make request to
        method: str = {"GET", "POST", "PUT", "DELETE"} from `JavaScript` global fetch())
        body: str = body as json string. Example, body=json.dumps(my_dict)
        headers: dict[str, str] = header as dict, will be converted to string...
            Example, headers=json.dumps({"Content-Type": "application/json"})
        fetch_kwargs: Any = any other keyword arguments to pass to `pyfetch` (will be passed to `fetch`)
    Return:
        response: pyodide.http.FetchResponse = use with .status or await.json(), etc.
    """
    kwargs = {"method": method, "mode": "cors"}  # CORS: https://en.wikipedia.org/wiki/Cross-origin_resource_sharing
    if body and method not in ["GET", "HEAD"]:
        kwargs["body"] = body
    if headers:
        kwargs["headers"] = headers
    kwargs.update(fetch_kwargs)

    return await pyfetch(url, **kwargs)

def download_db_file(url: str):
    """Downloads database using pyodide.http.pyfetch"""
    # loop = get_event_loop()
    # with NamedTemporaryFile("wb", suffix=".csv") as temp_file:
    #     temp_file: _TemporaryFileWrapper
    #     response = async_to_sync(request)(url, method="GET")
    #     buffer = response.arrayBuffer()
    #     temp_file.write(buffer)
    #     temp_file.flush()
    #     logger.info("Finished download, converting")
        # cursor_execute(f"CREATE TABLE clues AS SELECT * FROM '{temp_file.name}';")
    # cursor_execute(f"CREATE TABLE clues AS SELECT * FROM '{url}';")