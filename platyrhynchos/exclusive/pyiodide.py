from duckdb_wasm import connector
from asyncio import get_event_loop
from pyodide.http import pyfetch
# https://docs.pyscript.net/latest/guides/http-requests.html

def cursor_execute(sql, **kwargs): # type: ignore
    async def _execute():
        connection = await connector()
        return await connection.query(sql, kwargs)
    loop = get_event_loop()
    return loop.run_until_complete(_execute())