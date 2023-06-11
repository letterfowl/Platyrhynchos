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

  exolve-grid:
    $grid
  exolve-across:
    1 Running with placement, essentially, for single (3)
    3 Oddly fluent and entertaining (3)

  exolve-down:
    1 Retreating thief forgot to hide bananas (3)
    2 One suffering for a long time (3)

    # Note that you can provide an annotation after the closing parenthesis in
    # any clue, which will get shown after the solver "Reveal"s the clue.

  # The Exolve format has lots of additional features. See details in the
  # documentation at:
  #   https://github.com/viresh-ratnakar/exolve/blob/master/README.md
exolve-end
"""
)
