import os
from bib import Crossword
from random import random, shuffle
from keyboard import is_pressed
from time import perf_counter, time
from multiprocessing import cpu_count, Pool
from tqdm import tqdm

from visualize import gen_code, render

START_T = 1
SPEED = 1-0.015

SAMPLE_SIZE = 40
NOT_WORKING_LIMIT = 8

START_AM = 12

TARGET_SIZE = 33, 25
ADD_PLUS = True
PUZZLE_AMOUNT = 200

def goal(cross: Crossword) -> float:
    if cross is None:
        return 0
    letters = len(cross.letters)
    words = len(cross.words)
    size = cross.size

    return cross.crossings*letters/size


def find_best(tpl: tuple[Crossword, float, list[Crossword]]):
    cross, T, others = tpl

    golval = goal(cross)
    future = None
    for i in others:
        prod = cross.combineRandom(i, T)
        if cross.max[0] >= TARGET_SIZE[0] or cross.max[1] >= TARGET_SIZE[1]:
            continue

        if prod is None:
            continue
        if goal(prod) > golval:
            golval = goal(prod)
            future = prod
    return future

def getfiles():
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data/finish'):
        os.mkdir('data/finish')
    if not os.path.isdir('data/process'):
        os.mkdir('data/process')
    
    process_file = open(f'data/process/{int(time())}.csv', 'w')
    process_file.write("puzzle;turn;currtemperature;turntime;currgoalval;currsize;currratio;currcrossings;currlen\n")
    process_file.flush()
    finish_file = open(f'data/finish/{int(time())}.csv', 'w')
    finish_file.write("puzzle;turn_amount;sizeX;sizeY;finaltemperature;gentime;finalgoalval;finalsize;finalratio;finalcrossings;finallen\n")
    finish_file.flush()
    return process_file, finish_file

if __name__ == "__main__":
    CPUS = cpu_count()-2
    pool = Pool(CPUS)

    process_file, finish_file = getfiles()

    crosses = []
    for puzzle in tqdm(range(PUZZLE_AMOUNT)):

        timer_main = perf_counter()
        while True:
            c = list(Crossword.create(START_AM//2, ADD_PLUS))
            cr = [i.rotate() for i in Crossword.create(START_AM//2, ADD_PLUS)]

            s = list(c[1:])+list(cr[1:])
            shuffle(s)
            try:
                cross = sum(s, c[0]+cr[0])
            except TypeError:
                continue
            else:
                if cross.max[0] < TARGET_SIZE[0] and cross.max[1] < TARGET_SIZE[1]:
                    break

        T = START_T
        turn = 1
        golval = goal(cross)
        not_working = 0
        while True:  # golval<0.7:
            timer_small = perf_counter()

            future = None
            new = tuple(cross.createFor(SAMPLE_SIZE, ADD_PLUS))

            assigned = [(cross, T, new[i::CPUS]) for i in range(CPUS)]

            calculated = [i for i in pool.map(
                find_best, assigned) if i is not None]

            if random() < T/SAMPLE_SIZE:
                for i in calculated:
                    if goal(i) > golval:
                        future = cross
                        break
            elif len(calculated) > 0:
                future = max(calculated, key=goal)

            if future:
                not_working = 0
                cross = future
                golval = goal(future)
            else:
                not_working += 1
                if not_working > NOT_WORKING_LIMIT:
                    break
                T /= SPEED

            print(puzzle, turn,
                "%.4f" % round(T, 4),
                "%.4f" % round(perf_counter()-timer_small, 4),
                "%.4f" % round(golval, 4),
                "%.4f" % round(cross.size**0.5, 4),
                "%.4f" % round(len(cross.letters)/cross.size, 4),
                cross.crossings,
                len(cross.words),
                sep=";", file=process_file)

            T *= SPEED
            turn += 1

            if is_pressed('ctrl+shift+space'):
                break

        end = perf_counter()

        crosses.append(cross)
        print(puzzle, 
              turn, 
              cross.max[0], cross.max[1],
              "%.4f" % round(T, 4),
              end-timer_main,
              "%.4f" % round(golval, 4),
              "%.4f" % round(cross.size**0.5, 4),
              "%.4f" % round(len(cross.letters)/cross.size, 4),
              cross.crossings,
              len(cross.words),
              sep=";", file=finish_file)
        finish_file.flush()
        process_file.flush()

        if is_pressed('ctrl+shift+enter'):
            break

    finish_file.close()
    process_file.close()
    render(gen_code(crosses))
