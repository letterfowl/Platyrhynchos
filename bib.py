from __future__ import annotations
from json import load
import time
from random import sample, random, shuffle
from typing import Callable, ClassVar, Iterator
from dataclasses import dataclass, field
from functools import cached_property

with open('words.json', 'r', encoding='utf8') as f:
    WORDS = load(f)

WORDS_ITEMS = set(WORDS.items())


@dataclass(init=True, repr=True)
class Crossword(object):
    letters: dict[tuple[int, int], str]
    words: set[str]
    clueH: dict[tuple[int, int], str]
    clueV: dict[tuple[int, int], str] = field(default_factory=dict)
    crossings: int = 0

    # Static methods

    @staticmethod
    def _calc_size_change(A: tuple[int, int], B: tuple[int, int], maxB: tuple[int, int]) -> float:
        dv, dh = maxB[0] - B[0], maxB[1] - B[1]
        return (A[0]+dv)*(A[1]+dh)

    @staticmethod
    def _code_verify(A, B) -> bool:
        return True

    # Constructors

    @staticmethod
    def construct(word: str, clue: str) -> Crossword:
        return Crossword(
            letters={(0, i): j for i, j in enumerate(word)},
            words={word},
            clueH={(0, 0): clue}
        )

    @staticmethod
    def createFrom(hint_word: dict[str, str]) -> Iterator[Crossword]:
        for hint, word in hint_word.items():
            yield Crossword.construct(word, hint)

    @staticmethod
    def create(am: int, add: bool = False) -> Iterator[Crossword]:
        ch = sample(WORDS_ITEMS, k=am)
        for hint, word in ch:
            # print(word, "<-", hint, "\n")
            yield Crossword.construct(add*"+"+word+" ", hint)

    def createFor(self, am: int, add: bool = False) -> Iterator[Crossword]:
        ch = sample(WORDS_ITEMS - self.words, k=am)
        for hint, word in ch:
            # print(word, "<-", hint, "\n")
            yield Crossword.construct(add*"+"+word+" ", hint)
        

    # Magic methods

    def __str__(self) -> str:
        EMPTY = " "

        maxV, maxH = self.max
        minV, minH = self.min
        table = []
        for i in range(minV, maxV+1):
            t = []
            for j in range(minH, maxH+1):
                to_add = self.letters.get((i, j), EMPTY)
                if to_add == "+":
                    if (i, j) in self.clueH and (i, j) not in self.clueV:
                        to_add = "-"
                    elif (i, j) not in self.clueH and (i, j) in self.clueV:
                        to_add = "|"
                t.append(to_add)
            table.append("".join(t))
        return "\n".join(table)

    def __add__(self, other: Crossword) -> Crossword:
        return self.combine(other, 1)

    def combineWRotated(self, other: Crossword, T: float, key: Callable[[Crossword], float] = lambda x: -x.size) -> Crossword:
        a = self.combine(other, T)
        b = self.combine(other.rotate(), T)

        if not a:
            return b
        elif not b:
            return a
        else:
            return a if key(a) >= key(b) else b
        
    def combineRandom(self, other: Crossword, T: float) -> Crossword:
        if random() < 0.5:
            return self.combine(other, T)
        else:
            return self.combine(other.rotate(), T)

    def combine(self, other: Crossword, T: float) -> Crossword:
        if self.words & other.words:
            return None
        if random() > T:
            found = sorted(self._check_crossings(
                other), key=lambda x: self._calc_size_change(x[0], x[1], other.max))
        else:
            found = self._check_crossings(other)
        for p1, p2 in found:
            c1 = self.relative(p1)
            c2 = other.relative(p2)
            if all(c1.letters[i] == c2.letters[i] for i in c1.letters.keys() & c2.letters.keys()):
                csum = Crossword(
                    letters=c1.letters | c2.letters,
                    words=c1.words | c2.words,
                    clueV=c1.clueV | c2.clueV,
                    clueH=c1.clueH | c2.clueH,
                    crossings=sum(c1.letters[i] == c2.letters[i] for i in c1.letters.keys() & c2.letters.keys()) + c1.crossings + c2.crossings
                )
                return csum.absolute()

    # Properties

    @cached_property
    def max(self) -> tuple[int, int]:
        v, h = zip(*self.letters.keys())
        return max(v), max(h)

    @cached_property
    def size(self) -> int:
        a, b = self.max
        return (a+1)*(b+1)

    @cached_property
    def min(self) -> tuple[int, int]:
        v, h = zip(*self.letters.keys())
        return min(v), min(h)

    # Other

    def _get_crossable(self, letter: str) -> Iterator[tuple[int, int, tuple[bool]]]:
        for (v, h), l in self.letters.items():
            if l != letter:
                continue

            code = (
                # (v-1, h) in self.letters,
                # (v, h-1) in self.letters,
                # (v+1, h) in self.letters,
                # (v, h-1) in self.letters
            )
            yield v, h, code

    def _check_crossings(self, other: Crossword):
        possible_letters = set(self.letters.values()) & set(
            other.letters.values())
        for i in possible_letters:
            for v1, h1, code1 in self._get_crossable(i):
                for v2, h2, code2 in other._get_crossable(i):
                    if self._code_verify(code1, code2):
                        yield (v1, h1), (v2, h2)

    def relative(self, field: tuple[int, int]) -> Crossword:
        dv, dh = field
        return Crossword(
            letters={(v-dv, h-dh): i for (v, h), i in self.letters.items()},
            words=self.words,
            clueV={(v-dv, h-dh): i for (v, h), i in self.clueV.items()},
            clueH={(v-dv, h-dh): i for (v, h), i in self.clueH.items()},
            crossings=self.crossings
        )

    def absolute(self):
        m = self.relative(self.min)
        assert m.min == (0, 0), m.min
        return m

    def rotate(self) -> Crossword:
        return Crossword(
            letters={(j, i): letter for (i, j),
                     letter in self.letters.items()},
            words=self.words, 
            clueV={(j, i): clue for (i, j), clue in self.clueH.items()},
            clueH={(j, i): clue for (i, j), clue in self.clueV.items()},
            crossings=self.crossings
        )


if __name__ == '__main__':
    # from search import goal

    am = 5

    c = list(Crossword.create(am, True))
    cr = [i.rotate() for i in Crossword.create(am, True)]

    s = list(c[1:])+list(cr[1:])
    shuffle(s)
    d = sum(s, c[0]+cr[0])
    print(d)
    print(d.max)
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
