import os
from .libs.crossword_addable import CrosswordAddable
from string import ascii_letters

HEADER = r"""
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}

\usepackage[unboxed]{cwpuzzle}
\usepackage[top=15mm,bottom=15mm,left=15mm,right=3cm,twoside]{geometry}
\usepackage{adjustbox}

\newcommand\drarr{$\rightarrow \!\!\!\!\! \downarrow$}
\newcommand\rarr{$\rightarrow$}
\newcommand\darr{$\downarrow$}

\begin{document}

"""
FOOTER = r"""
\end{document}
"""

EMPTY = r"*"
CLEANER = {
    "\\": "\\textbackslash",
    "&": "\\&",
    "%": "\\%",
    "$": "\\$",
    "_": "\\",
    "{": "\\{",
    "}": "\\}",
    "~": "\\textasciitilde",
    "^": "\\textasciicircum",
}
_cleantable = CLEANER|{" ": EMPTY, None: EMPTY}
_cleanhint = CLEANER|{"#": "\\#"}
def cleanhint(s: str) -> str:
    for i,j in _cleanhint.items():
        s = s.replace(i,j)
    return s
 
def gen_table(cross: CrosswordAddable):
    SYMBOLS = ascii_letters+EMPTY+"ąęóśłżźćń"

    hintnum = 0
    maxV, maxH = cross.max
    minV, minH = cross.min

    table = []
    hintsH = []
    hintsV = []

    for i in range(maxV+1):
        t = []
        for j in range(maxH+1):
            
            # Przetwarzanie wstępne
            add_symbol = cross.letters.get((i, j))
            add_symbol = _cleantable.get(add_symbol, add_symbol)


            # Obsługa podpowiedzi
            new_clues_horizontal = cross.clues_horizontal.get((i, j))
            new_clues_vertical = cross.clues_vertical.get((i, j))

            if new_clues_horizontal or new_clues_vertical:
                hintnum += 1
                hint = f"[{hintnum}]"
            else:
                hint = ""

            if new_clues_horizontal:
                hintsH.append(r"\Clue{%d}{}{%s}" % (hintnum, cleanhint(new_clues_horizontal)))
            if new_clues_vertical:
                hintsV.append(r"\Clue{%d}{}{%s}" % (hintnum, cleanhint(new_clues_vertical)))
            # Dodawanie strzałek dla +
            if add_symbol == "+":
                if new_clues_horizontal and not new_clues_vertical:
                    add_symbol = r"[S]\rarr"
                elif not new_clues_horizontal and new_clues_vertical:
                    add_symbol = r"[S]\darr"
                else:
                    add_symbol = r"[S]\drarr"
            elif add_symbol == "#":
                add_symbol = r'[][,]{ }'
            elif add_symbol not in SYMBOLS:
                add_symbol = f"[][S]{add_symbol}" 

            # Dodawanie wiersza
            t.append("".join((
                hint,
                add_symbol
            )))
        table.append("|"+"\t|".join(t)+"\t|.")
    return table, hintsH, hintsV 

def _gen_code(cross: CrosswordAddable):
    table, hintsH, hintsV = gen_table(cross)
    rtable = r"\noindent\begin{Puzzle}{%d}{%d}%s\end{Puzzle}" % (cross.max[1], cross.max[0], "\n".join(table))
    rhintsH = r"\begin{PuzzleClues}{\textbf{Poziome}\\}%s\end{PuzzleClues}" % ("\n".join(hintsH))
    rhintsV = r"\begin{PuzzleClues}{\textbf{Pionowe}\\}%s\end{PuzzleClues}" % ("\n".join(hintsV))
    return rtable, rhintsH, rhintsV

    
def gen_code(cross: list[CrosswordAddable]) -> str:
    strings = [HEADER+"\n\n"]
    for n, i in enumerate(cross):
        rtable, rhintsH, rhintsV = _gen_code(i)
        strings.append("\n\n".join(( 
                    r"\section*{Krzyżówka %d}" % (n+1),
                    rtable, 
                    r"\newpage",
                    rhintsH, rhintsV, 
                    )))
    return r"\newpage".join(strings)+"\n\n"+FOOTER

#\maxsizebox{\textwidth}{\textheight}{

def render(code: str) -> None:
    with open('tmp/cross.tex', 'w', encoding='utf8') as f:
        f.write(code)
    
    os.system('xelatex tmp/cross.tex -quiet -output-directory=tmp')
