"""
Implements the Alphabit system for row filtering in SQL
Also contains `MIN_ALPHABIT` and `MAX_ALPHABIT` constants that represent a string with no letters
and a string with all letters.
"""
from string import ascii_uppercase
from typing import Optional

from bitarray import bitarray

class Alphabit:
    """
    A wrapper over `bitarray` object to parse into the database.

    `LETTER_ORDER` stores the order of letters in the `bitarray`.
    By default it's the reverse of the alphabet. It shouldn't have any effect on speed.
    """

    LETTER_ORDER = ascii_uppercase[::-1]

    def __init__(self, initializer: str = "", bits: Optional[bitarray] = None) -> None:
        """
        Initializes an `Alphabit` object. Requires initializer or bits arguments.
        If none of them are provided, equivalend of `MIN_ALPHABIT` will be produced

        Keyword Arguments:
            initializer -- String to be represented (default: {""})
            bits -- `bitarray` to be wrapped, prioritized over initializer (default: {None})
        """
        if bits is not None:
            self.bittarray = bits
        else:
            letters_in_word = set(initializer.upper())
            self.bittarray = bitarray((letter in letters_in_word for letter in self.LETTER_ORDER))

    def to_db(self) -> str:
        """Generates a database Alphabit value of a word"""
        return self.bittarray.to01()

    def to_query(self) -> str:
        """Generates an Alphabit query to be used in SQL"""
        return (~self.bittarray).to01()
    
    def as_letters(self) -> str:
        return "".join(letter for letter, bit in zip(self.LETTER_ORDER, self.bittarray) if bit)


MIN_ALPHABIT = Alphabit("")
MAX_ALPHABIT = Alphabit(ascii_uppercase)
