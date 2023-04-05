from bitarray import bitarray
from string import ascii_uppercase

MIN_ALPHABIT = bitarray(len(ascii_uppercase))
MIN_ALPHABIT.setall(0)

def to_alphabit(word: str) -> bitarray:
    letters_in_word = set(word.upper())
    return bitarray((letter in letters_in_word for letter in ascii_uppercase[::-1]))

def adapt_alphabit(p: bitarray) -> bytes:
    """Maps a bitarray into a blob"""
    return p.tobytes()

def convert_alphabit(p: bytes) -> bitarray:
    array = bitarray(len(ascii_uppercase))
    array.frombytes(p)
    return array
        
MAX_ALPHABIT = to_alphabit(ascii_uppercase)