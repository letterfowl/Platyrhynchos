from string import Template

EXOLVE_TEMPLATE: Template = Template(
    """
exolve-begin
  exolve-id: exolve-example
  exolve-title: Exolve Example

  # Uncomment and edit the next two lines if you want to show the setter's name
  # and/or show a copyright notice.
  exolve-setter: letterfowl
  exolve-copyright: 2023 All rights reserved.

  exolve-width: $width
  exolve-height: $height
  exolve-option: allow-chars:-❈%

  exolve-grid:
    $grid

  exolve-option: ignore-unclued
  # Note that you can provide an annotation after the closing parenthesis in
  # any clue, which will get shown after the solver "Reveal"s the clue.

  # The Exolve format has lots of additional features. See details in the
  # documentation at:
  #   https://github.com/viresh-ratnakar/exolve/blob/master/README.md
exolve-end
"""
)


def char_for_grid(char: str):
    match char:
        case "-", "$":
            return f"{char}!"
        case " ":
            return "❈!"
        case _:
            return char
