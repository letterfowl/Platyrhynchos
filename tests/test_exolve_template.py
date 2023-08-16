import pytest

from platyrhynchos.crossword.exolve_template import char_for_grid


@pytest.mark.parametrize("char, expected", [("-", "-!"), ("$", "$!"), (" ", "#!"), ("A", "A"), ("1", "1"), ("%", "%")])
def test_char_for_grid(char, expected):
    """
    Test the char_for_grid function.

    This function tests the char_for_grid function with various input parameters.

    Args:
        char (str): The input character to be tested.
        expected (str): The expected output of the function.
    """
    assert char_for_grid(char) == expected
