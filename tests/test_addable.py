from unittest import TestCase
from platyrhynchos.crossword.addable import CrosswordAddable

class TestBuild(TestCase):
    def test_build(self):
        self.assertEqual(
            list(CrosswordAddable.createFrom({"1": "abc", "2": "cdef", "3": "abcdefg"})),
            [
                CrosswordAddable(
                    letters={(0, 0): 'a', (1, 0): 'b', (2, 0): 'c'},
                    clues_horizontal={(0, 0): '1'},
                    clues_vertical={},
                ),
                CrosswordAddable(
                    letters={(0, 0): 'c', (1, 0): 'd', (2, 0): 'e', (3, 0): 'f'},
                    clues_horizontal={(0, 0): '2'},
                    clues_vertical={},
                ),
                CrosswordAddable(
                    letters={
                        (0, 0): 'a',
                        (1, 0): 'b',
                        (2, 0): 'c',
                        (3, 0): 'd',
                        (4, 0): 'e',
                        (5, 0): 'f',
                        (6, 0): 'g',
                    },
                    clues_horizontal={(0, 0): '3'},
                    clues_vertical={},
                ),
            ],
        )