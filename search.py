from os import extsep
from bib import Crossword
from random import random, sample, shuffle
from keyboard import is_pressed

START_T = 1
SPEED = 1-0.01

SAMPLE_SIZE = 30
START_AM = 20


def goal(cross) -> float:
    letters = len(cross.letters)
    words = len(cross.words)
    size = cross.size
    
    return letters/size #* -1-abs(words-GOAL_SIZE) 


if __name__=="__main__":
    while True:
        c = [i for i in Crossword.create(START_AM//2, True)]
        cr = [i.rotate() for i in Crossword.create(START_AM//2, True)]

        s = list(c[1:])+list(cr[1:])
        shuffle(s)
        try:
            cross = sum(s, c[0]+cr[0])
        except TypeError:
            continue
        else:
            break
    
    T = START_T
    turn = 1
    golval = goal(cross)
    while golval<0.7:
        new = cross.createFor(SAMPLE_SIZE, True)
        future = None
        
        for i in sample(tuple(new), SAMPLE_SIZE):
                
            prod = cross.combineRandom(i, T)
            
            if prod is None: 
                continue
            if goal(prod)>golval:
                golval = goal(prod)
                future = prod
                if random() < T/SAMPLE_SIZE:
                    break
                
        if future:
            cross = future
            golval = goal(future)
        else:
            T /= SPEED 
        
        print(turn, T, golval, cross.size**0.5, len(cross.words), len(cross.letters)/cross.size, sep="; ")
        
        T *= SPEED
        turn += 1
        
        if is_pressed('space'):
            break
        
    print(str(cross))