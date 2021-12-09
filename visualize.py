import os
from bib import Crossword
from string import ascii_letters

HEADER = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\usepackage[unboxed]{cwpuzzle}
\usepackage[left=5mm, right=5mm, bottom=5mm, top=5mm]{geometry}
\usepackage{adjustbox}

\newcommand\drarr{$\rightarrow \!\!\!\!\! \downarrow$}
\newcommand\rarr{$\rightarrow$}
\newcommand\darr{$\downarrow$}

\begin{document}

"""
FOOTER = r"""
\end{document}
"""

def gen_table(cross: Crossword):
    EMPTY = r"*"
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
            add_symbol = {
                " ": EMPTY,
                None: EMPTY,
            }.get(add_symbol, add_symbol)


            # Obsługa podpowiedzi
            new_clueH = cross.clueH.get((i, j))
            new_clueV = cross.clueV.get((i, j))

            if new_clueH or new_clueV:
                hintnum += 1
                hint = f"[{hintnum}]"
                if new_clueH:
                    hintsH.append(r"\Clue{%d}{}{%s}" % (hintnum, new_clueH))
                if new_clueV:
                    hintsV.append(r"\Clue{%d}{}{%s}" % (hintnum, new_clueV))    
            else:
                hint = ""

            # Dodawanie strzałek dla +
            if add_symbol == "+":
                if new_clueH and not new_clueV:
                    add_symbol = r"[S]\rarr"
                elif not new_clueH and new_clueV:
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


def gen_code(cross: Crossword) -> str:
    table, hintsH, hintsV = gen_table(cross)
    rtable = r"\noindent\begin{Puzzle}{%d}{%d}%s\end{Puzzle}" % (cross.max[1], cross.max[0], "\n".join(table))
    rhintsH = r"\begin{PuzzleClues}{\textbf{Poziome}\\}%s\end{PuzzleClues}" % ("\n".join(hintsH))
    rhintsV = r"\begin{PuzzleClues}{\textbf{Pionowe}\\}%s\end{PuzzleClues}" % ("\n".join(hintsV))
    return "\n\n".join((HEADER, 
                        rtable, 
                        r"\newpage",
                        rhintsH, rhintsV, 
                        FOOTER))

#\maxsizebox{\textwidth}{\textheight}{

def render(code: str) -> None:
    with open('tmp/cross.tex', 'w', encoding='utf8') as f:
        f.write(code)
    
    os.system('xelatex tmp/cross.tex -quiet -output-directory=tmp')
