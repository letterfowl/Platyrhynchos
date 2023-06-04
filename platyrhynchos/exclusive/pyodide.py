from bitarray import bitarray
from supabase4js import getRandom, getRegex, getRegexWithAlphabit
from pyodide.webloop import WebLoop
from time import sleep

def download_db(url: str):
    """Doesn't do anything lmao"""
    pass

def run_in_webloop(func):
    def wrapper(*args, **kwargs):
        task = WebLoop().run_until_complete(func(*args, **kwargs))
        while not task.done():
            sleep(0.1)
        return task.result()
    return wrapper

get_random = run_in_webloop(getRandom)
get_regex = run_in_webloop(getRegex)
get_regex_w_alphabit = run_in_webloop(getRegexWithAlphabit)
