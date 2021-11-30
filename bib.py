from __future__ import annotations
from json import load
from random import choices, shuffle
from typing import Iterator
from dataclasses import dataclass, field

with open('words.json', 'r', encoding='utf8') as f:
    WORDS = load(f)
    
WORDS_ITEMS = list(WORDS.items())

@dataclass(init=True, repr=True)
class Crossword(object):
    letters: dict[tuple[int, int], str]
    clueV: dict[tuple[int, int], str]
    clueH: dict[tuple[int, int], str] = field(default_factory=dict)

    # Static methods

    @staticmethod
    def construct(word: str, clue: str) -> Crossword:
        return Crossword(
            letters = {(0,i):j for i,j in enumerate(word)},
            clueH = {(0,0): clue},
            clueV = {}
        )
    
    @staticmethod
    def create_from(hint_word: dict[str, str]) -> Iterator[Crossword]:
        for hint, word in hint_word.items():
            yield Crossword.construct(word, hint)
    
    @staticmethod
    def create(am: int) -> Iterator[Crossword]:
        ch = choices(WORDS_ITEMS, k=am)
        for hint, word in ch:
            print(word, "<-", hint, "\n")
            yield Crossword.construct(word, hint)
    
    # Magic methods
    
    def __str__(self) -> str:
        EMPTY = " "
        
        maxV, maxH = self.max()
        minV, minH = self.min()
        table = []
        for i in range(minV, maxV+1):
            t = [self.letters.get((i,j), EMPTY) for j in range(minH, maxH+1)]
            table.append("".join(t))
        return "\n".join(table)
    
    def __add__(self, other: Crossword) -> Crossword:
        for p1, p2 in self._check_crossings(other):
            c1 = self.relative(p1)
            c2 = other.relative(p2)
            if all(c1.letters[i] == c2.letters[i] for i in c1.letters.keys() & c2.letters.keys()):
                csum = Crossword(
                    letters= c1.letters | c2.letters,
                    clueV= c1.clueV | c2.clueV,
                    clueH= c1.clueH | c2.clueH
                )
                return csum.absolute()
                
        
    
    # Other
    
    def _get_crossable(self, letter: str) -> Iterator[tuple[int, int, tuple[bool]]]:
        for (v,h), l in self.letters.items():
            if l != letter:
                continue
            
            code = (
                (v-1, h) in self.letters,
                (v, h-1) in self.letters,
                (v+1, h) in self.letters,
                (v, h-1) in self.letters
                )
            yield v, h, code
    
    
    @staticmethod
    def _code_verify(A, B) -> bool:
        if any(A[n] and B[n] for n in range(len(A))):
            return False
        
        return not ((A[0] and B[2]) or (A[1] and B[3]) or (B[0] and A[2]) or (B[1] and A[3]))
    
    def _check_crossings(self, other: Crossword):
        possible_letters = set(self.letters.values()) & set(other.letters.values())
        for i in possible_letters:
            for v1, h1, code1 in self._get_crossable(i):
                for v2, h2, code2 in other._get_crossable(i):
                    if self._code_verify(code1, code2):
                        yield (v1, h1), (v2, h2)
                    
    def relative(self, field: tuple[int, int], minus: bool = True) -> Crossword:
        dv, dh = field
        if minus:
            dv = -dv
            dh = -dh
        return Crossword(
            letters = {(v+dv, h+dh):i for (v,h), i in self.letters.items()},
            clueV = {(v+dv, h+dh):i for (v,h), i in self.clueV.items()},
            clueH = {(v+dv, h+dh):i for (v,h), i in self.clueH.items()}
        )
        
    def absolute(self):
        m = self.min()
        return self.relative(m, False)
        
    
    def rotate(self) -> Crossword:
        return Crossword(
            letters = {(j,i):letter for (i,j), letter in self.letters.items()},
            clueV = {(j,i):clue for (i,j), clue in self.clueH.items()},
            clueH = {(j,i):clue for (i,j), clue in self.clueV.items()},
        )
        
    def max(self) -> tuple[int, int]:
        v, h = zip(*self.letters.keys())
        return max(v), max(h)
    
    def min(self) -> tuple[int, int]:
        v, h = zip(*self.letters.keys())
        return min(v), min(h)
    
    
am = 10

c = [i for i in Crossword.create(am)]
cr = [i.rotate() for i in Crossword.create(am)]

s = list(c[1:])+list(cr[1:])
shuffle(s)
print(str(sum(s, c[0]+cr[0])))