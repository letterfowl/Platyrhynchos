from time import sleep

from bitarray import bitarray
from pyodide.webloop import WebLoop
from supabase4js import getRandom, getRegex, getRegexWithAlphabit


def download_db(url: str):
    """Doesn't do anything lmao"""
    pass


async def get_random(max_size: int):
    return await getRandom(max_size)


async def get_regex(regex: str, previous: list[str] = []):
    previous = ",".join(previous or [])
    return await getRegex(regex, previous)


async def get_regex_w_alphabit(regex: str, alphabit: str, previous: list[str] = None):
    previous = ",".join(previous or [])
    return await getRegexWithAlphabit(regex, alphabit, previous)
