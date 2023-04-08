from typing import Optional
from bitarray import bitarray
from string import ascii_uppercase

class Alphabit:
    LETTER_ORDER = ascii_uppercase[::-1]
    
    def __init__(self, initializer: str = "", bits: Optional[bitarray] = None) -> None:
        if bits is not None:
            self.bittarray=bits
        else:
            letters_in_word = set(initializer.upper())
            self.bittarray=bitarray((letter in letters_in_word for letter in self.LETTER_ORDER))
        
    def to_db(self) -> str:
        return self.bittarray.to01()
    
    def neg(self):
        return Alphabit(bits=~self.bittarray)
    
    def to_query(self) -> str:
        return f"'{(~self.bittarray).to01()}'::BIT"

MIN_ALPHABIT = Alphabit("")
MAX_ALPHABIT = Alphabit(ascii_uppercase)
