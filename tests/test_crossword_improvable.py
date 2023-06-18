from platyrhynchos.crossword.improvable import CrosswordImprovable

def creation_and_rotation(letters, width, height, words_horizontal):
    result = CrosswordImprovable(letters, height, width, words_horizontal)
    result.rotate()
    assert result.max_h == width
    assert result.max_v == height
    return result

def test_rotate_2x2():
    letters = {
        (0, 0): "A",
        (0, 1): "B",
        (1, 0): "C",
        (1, 1): "D",
    }
    words_horizontal = {"AB": {(0, 0), (0, 1)}, "CD": {(1, 0), (1, 1)}}
    crossword = creation_and_rotation(letters, 2, 2, words_horizontal)
    assert crossword.letters == {
        (0, 0): "A",
        (1, 0): "B",
        (0, 1): "C",
        (1, 1): "D",
    }
    assert crossword.words_vertical == {"AB": {(0, 0), (1, 0)}, "CD": {(0, 1), (1, 1)}}
    assert crossword.words_horizontal == {}

def test_rotate_3x2():
    letters = {
        (0, 0): "A",
        (0, 1): "B",
        (0, 2): "C",
        (1, 0): "D",
        (1, 1): "E",
        (1, 2): "F",
    }
    words_horizontal = {"ABC": {(0, 0), (0, 1), (0, 2)}, "DEF": {(1, 0), (1, 1), (1, 2)}}
    crossword = creation_and_rotation(letters, 2, 3, words_horizontal)
    assert crossword.letters == {
        (0, 0): "A",
        (1, 0): "B",
        (2, 0): "C",
        (0, 1): "D",
        (1, 1): "E",
        (2, 1): "F",
    }
    assert crossword.words_vertical == {"ABC": {(0, 0), (1, 0), (2, 0)}, "DEF": {(0, 1), (1, 1), (2, 1)}}
    assert crossword.words_horizontal == {}