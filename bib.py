from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from json import load
from random import choice, random, sample, shuffle
from typing import Callable, Iterator

with open("words.json", "r", encoding="utf8") as f:
    WORDS = load(f)

WORDS_ITEMS = set(WORDS.items())


@dataclass(init=True, repr=True)
class Crossword(object):
    letters: dict[tuple[int, int], str]
    wordsH: dict[str, set[tuple[int, int]]]
    clueH: dict[tuple[int, int], str]
    wordsV: dict[str, set[tuple[int, int]]] = field(default_factory=dict)
    clueV: dict[tuple[int, int], str] = field(default_factory=dict)
    crossings: set[tuple[int, int]] = field(default_factory=set)

    # Static methods

    @staticmethod
    def _calc_size_change(A: tuple[int, int], B: tuple[int, int], maxB: tuple[int, int]) -> float:
        dv, dh = maxB[0] - B[0], maxB[1] - B[1]
        return (A[0] + dv) * (A[1] + dh)

    @staticmethod
    def _code_verify(A, B) -> bool:
        return True

    # Constructors

    @staticmethod
    def construct(word: str, clue: str) -> Crossword:
        return Crossword(
            letters={(0, i): j for i, j in enumerate(word)},
            wordsH={word: {(0, i) for i in range(len(word))}},
            clueH={(0, 0): clue},
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
            yield Crossword.construct(add * "+" + word + " ", hint)

    def createFor(self, am: int, add: bool = False) -> Iterator[Crossword]:
        ch = sample(WORDS_ITEMS - self.words.keys(), k=am)
        for hint, word in ch:
            # print(word, "<-", hint, "\n")
            yield Crossword.construct(add * "+" + word + " ", hint)

    # Magic methods

    def __str__(self) -> str:
        EMPTY = " "

        maxV, maxH = self.max
        minV, minH = self.min
        table = []
        for i in range(minV, maxV + 1):
            t = []
            for j in range(minH, maxH + 1):
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

    # Properties

    @cached_property
    def words(self) -> dict[str, set[tuple[int, int]]]:
        return self.wordsH | self.wordsV

    @cached_property
    def max(self) -> tuple[int, int]:
        v, h = zip(*self.letters.keys())
        return max(v), max(h)

    @cached_property
    def size(self) -> int:
        a, b = self.max
        return (a + 1) * (b + 1)

    @cached_property
    def min(self) -> tuple[int, int]:
        v, h = zip(*self.letters.keys())
        return min(v), min(h)

    # Getters

    def getIntersecting(self, word: str) -> set[str]:
        coords = self.words[word] & self.crossings
        return {w for w, c in self.words.items() if w != word and any(coords & c)}

    # Crossword operations

    def combineWRotated(
        self, other: Crossword, T: float, key: Callable[[Crossword], float] = lambda x: -x.size
    ) -> Crossword:
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

    def combine(self, other: Crossword, T: float = 0) -> Crossword:
        if self.words.keys() & other.words.keys():
            return None
        if random() > T:
            found = sorted(self._check_crossings(other), key=lambda x: self._calc_size_change(x[0], x[1], other.max))
        else:
            found = self._check_crossings(other)
        for p1, p2 in found:
            c1 = self.relative(p1)
            c2 = other.relative(p2)
            if all(c1.letters[i] == c2.letters[i] for i in c1.letters.keys() & c2.letters.keys()):
                csum = Crossword(
                    letters=c1.letters | c2.letters,
                    wordsH=c1.wordsH | c2.wordsH,
                    clueV=c1.clueV | c2.clueV,
                    wordsV=c1.wordsV | c2.wordsV,
                    clueH=c1.clueH | c2.clueH,
                    crossings={i for i in c1.letters.keys() & c2.letters.keys() if c1.letters[i] == c2.letters[i]}
                    | c1.crossings
                    | c2.crossings,
                )
                return csum.absolute()

    def remove(self, word: str) -> Crossword:
        letter_coords = self.words.get(word, None)
        if letter_coords is None:
            raise KeyError("Nie ma takiego słowa")
        new = Crossword(
            letters={
                coord: i for coord, i in self.letters.items() if coord not in letter_coords or coord in self.crossings
            },
            wordsV={w: i for w, i in self.wordsV.items() if word != w},
            clueV=self.clueV
            if word in self.wordsH
            else {coord: i for coord, i in self.clueV.items() if coord not in letter_coords},
            wordsH={w: i for w, i in self.wordsH.items() if word != w},
            clueH=self.clueH
            if word in self.wordsV
            else {coord: i for coord, i in self.clueH.items() if coord not in letter_coords},
            crossings={coords for coords in self.crossings if coords not in letter_coords},
        )
        if len(new.words) == 0:
            return None
        return new.absolute()

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
        possible_letters = set(self.letters.values()) & set(other.letters.values())
        for i in possible_letters:
            for v1, h1, code1 in self._get_crossable(i):
                for v2, h2, code2 in other._get_crossable(i):
                    if self._code_verify(code1, code2):
                        yield (v1, h1), (v2, h2)

    def relative(self, field: tuple[int, int]) -> Crossword:
        dv, dh = field
        return Crossword(
            letters={(v - dv, h - dh): i for (v, h), i in self.letters.items()},
            wordsV={word: {(v - dv, h - dh) for (v, h) in i} for word, i in self.wordsV.items()},
            clueV={(v - dv, h - dh): i for (v, h), i in self.clueV.items()},
            clueH={(v - dv, h - dh): i for (v, h), i in self.clueH.items()},
            wordsH={word: {(v - dv, h - dh) for (v, h) in i} for word, i in self.wordsH.items()},
            crossings={(v - dv, h - dh) for (v, h) in self.crossings},
        )

    def absolute(self):
        m = self.relative(self.min)
        assert m.min == (0, 0), m.min
        return m

    def rotate(self) -> Crossword:
        return Crossword(
            letters={(j, i): letter for (i, j), letter in self.letters.items()},
            wordsH={word: {(h, v) for (v, h) in i} for word, i in self.wordsV.items()},
            wordsV={word: {(h, v) for (v, h) in i} for word, i in self.wordsH.items()},
            clueV={(j, i): clue for (i, j), clue in self.clueH.items()},
            clueH={(j, i): clue for (i, j), clue in self.clueV.items()},
            crossings={(j, i) for (i, j) in self.crossings},
        )


if __name__ == "__main__":
    # from search import goal

    am = 5

    c = list(Crossword.create(am, True))
    cr = [i.rotate() for i in Crossword.create(am, True)]

    s = list(c[1:]) + list(cr[1:])
    shuffle(s)
    d = sum(s, c[0] + cr[0])
    print(d)
    print(d.max)

    a = d
    for i in d.words:
        print(i)
        a = a.remove(i)
        print(a)
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
