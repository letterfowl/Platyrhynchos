from __future__ import annotations
from json import load
from random import sample, random, shuffle
from typing import Callable, Iterable, Optional, TypeVar
from dataclasses import dataclass, field
from .base import Crossword
from ..commons import Coord

CrosswordAddableT = TypeVar("CrosswordAddableT", bound="CrosswordAddable")

with open('words.json', 'r', encoding='utf8') as f:
    WORDS = load(f)

WORDS_ITEMS = set(WORDS.items())

@dataclass(init=True, repr=True)
class CrosswordAddable(Crossword):
    clues_horizontal: dict[tuple[int, int], str] = field(default_factory=dict)
    clues_vertical: dict[tuple[int, int], str] = field(default_factory=dict)

    # Static methods

    @staticmethod
    def _calc_size_change(A: Coord, B: Coord, maxB: Coord) -> float:
        dv, dh = maxB[0] - B[0], maxB[1] - B[1]
        return (A[0]+dv)*(A[1]+dh)

    @staticmethod
    def _code_verify(A, B) -> bool:
        return True

    # Constructors

    @staticmethod
    def construct(word: str, clue: str) -> CrosswordAddable:
        return CrosswordAddable(
            letters={Coord((0, i)): j for i, j in enumerate(word)},
            words_horizontal={word:{Coord((0, i)) for i in range(len(word))}},
            clues_horizontal={Coord((0, 0)): clue}
        )

    @staticmethod
    def createFrom(hint_word: dict[str, str]) -> Iterable[CrosswordAddable]:
        for hint, word in hint_word.items():
            yield CrosswordAddable.construct(word, hint)

    @staticmethod
    def create(am: int, add: bool = False) -> Iterable[CrosswordAddable]:
        ch = sample(WORDS_ITEMS, k=am)
        for hint, word in ch:
            # print(word, "<-", hint, "\n")
            yield CrosswordAddable.construct(add*"+"+word+" ", hint)

    def createFor(self, word_amount: int, add: bool = False) -> Iterable[CrosswordAddable]:
        ch = sample(WORDS_ITEMS - self.words.keys(), k=word_amount)
        for hint, word in ch:
            # print(word, "<-", hint, "\n")
            yield CrosswordAddable.construct(add*"+"+word+" ", hint)
        

    # Magic methods

    def __str__(self) -> str:
        EMPTY = " "

        # pylint: disable=unpacking-non-sequence
        max_vertical, max_horizontal = self.max
        # pylint: disable=unpacking-non-sequence
        min_vertical, min_horizontal = self.min
        table = []
        for i in range(min_vertical, max_vertical+1):
            t = []
            for j in range(min_horizontal, max_horizontal+1):
                to_add = self.letters.get(Coord((i, j)), EMPTY)
                if to_add == "+":
                    if (i, j) in self.clues_horizontal and (i, j) not in self.clues_vertical:
                        to_add = "-"
                    elif (i, j) not in self.clues_horizontal and (i, j) in self.clues_vertical:
                        to_add = "|"
                t.append(to_add)
            table.append("".join(t))
        return "\n".join(table)

    def __add__(self, other: Crossword) -> Optional[CrosswordAddable]:
        return self.combine(other, 1)
    
    # Getters

    def getIntersecting(self, word: str) -> set[str]:
        coords = self.words[word] & self.crossings
        return {w for w, c in self.words.items() if w != word and any(coords & c)}

    # Crossword operations

    def combineWRotated(self, other: Crossword, T: float, key: Callable[[Crossword], float] = lambda x: -x.size) -> CrosswordAddable:
        a = self.combine(other, T)
        b = self.combine(other.rotate(), T)

        if not a:
            return b
        elif not b:
            return a
        else:
            return a if key(a) >= key(b) else b
        
    def combineRandom(self, other: Crossword, T: float) -> CrosswordAddable:
        if random() < 0.5:
            return self.combine(other, T)
        else:
            return self.combine(other.rotate(), T)

    def combine(self, other: CrosswordAddable, T: float = 0) -> Optional[CrosswordAddable]:
        if self.words.keys() & other.words.keys():
            return None
        if random() > T:
            found = sorted(self._check_crossings(
                other), key=lambda x: self._calc_size_change(x[0], x[1], other.max))
        else:
            found = self._check_crossings(other)
        for p1, p2 in found:
            # TODO: fix
            c1 = self.relative(p1)
            c2 = other.relative(p2)
            if all(c1.letters[i] == c2.letters[i] for i in c1.letters.keys() & c2.letters.keys()):
                csum = CrosswordAddable(
                    letters=c1.letters | c2.letters,
                    words_horizontal=c1.words_horizontal | c2.words_horizontal,
                    clues_vertical=c1.clues_vertical |  c2.clues_vertical,
                    words_vertical=c1.words_vertical | c2.words_vertical,
                    clues_horizontal=c1.clues_horizontal | c2.clues_horizontal,
                    crossings= {i for i in c1.letters.keys() & c2.letters.keys() if c1.letters[i] == c2.letters[i]} | c1.crossings | c2.crossings
                )
                return csum.absolute()

    # TODO: add clues to the rotate function

    def remove(self, word: str) -> Optional[CrosswordAddable]:
        letter_coords = self.words.get(word, None)
        if letter_coords is None:
            raise KeyError("Nie ma takiego słowa")
        new = CrosswordAddable(
            letters={coord: i for coord, i in self.letters.items() if coord not in letter_coords or coord in self.crossings},
            words_vertical={w: i for w, i in self.words_vertical.items() if word != w},
            clues_vertical=self.clues_vertical if word in self.words_horizontal else {coord: i for coord, i in self.clues_vertical.items() if coord not in letter_coords},
            words_horizontal={w: i for w, i in self.words_horizontal.items() if word != w},
            clues_horizontal=self.clues_horizontal if word in self.words_vertical else {coord: i for coord, i in self.clues_horizontal.items() if coord not in letter_coords},
            crossings={coords for coords in self.crossings if coords not in letter_coords}
        )
        if len(new.words) == 0:
            return None
        return new.absolute()
            
    # Other

    def _get_crossable(self, letter: str) -> Iterable[Coord]:
        for (v, h), l in self.letters.items():
            if l != letter:
                continue
            yield Coord((v, h))

    def _check_crossings(self, other: Crossword):
        possible_letters = set(self.letters.values()) & set(
            other.letters.values())
        for i in possible_letters:
            for v1, h1, code1 in self._get_crossable(i):
                for v2, h2, code2 in other._get_crossable(i):
                    if self._code_verify(code1, code2):
                        yield (v1, h1), (v2, h2)



def main():
    # from search import goal

    am = 5

    c = list(CrosswordAddable.create(am, True))
    cr = [i.rotate() for i in CrosswordAddable.create(am, True)]

    s = [i for i in list(c[1:])+list(cr[1:]) if i is not None]
    shuffle(s)
    if (starter := c[0]+cr[0]) is None:
        return
    d = sum(s, starter)
    print(d)
    print(d.max)
    
    a = d
    for i in d.words:
        print(i)
        a_ = a.remove(i)
        if a_ is not None:
            a = a_
    # print(goal(d))

    # sims = 500
    # for am in range(5, 101, 5):
    #     failed = 0
    #     bigs = 0
    #     bigt = 0
    #     for i in range(sims):
    #         size = None
    #         start = time.time()
    #         try:
    #             c = [i for i in Crossword.create(am, True)]
    #             cr = [i.rotate() for i in Crossword.create(am, True)]

    #             s = list(c[1:])+list(cr[1:])
    #             shuffle(s)
    #             cros = sum(s, c[0]+cr[0])
    #             size = cros.max[0]-cros.min[0], cros.max[1]-cros.min[1]
    #         except TypeError:
    #             failed+=1
    #         bigt += time.time()-start
    #         bigs += size[0]*size[1] if size else 0
    #     print(am, failed/sims, bigt/sims, (bigs/(sims-failed))**0.5)

if __name__=="__main__":
    main()