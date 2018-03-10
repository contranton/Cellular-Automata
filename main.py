"""Main process logic"""

import cProfile

from cell import CellConfig
from board import Board
from graphics import GraphicSys
from gpu import CudaSys

import patterns


def cfg_forest_fire(p, f):
    CFG = CellConfig()
    CFG.possible_states = {0: "Empty", 1: "Tree", 2: "Burning"}

    p = 0.01
    f = 0.0001

    CFG.rules = "1:2(12345678)2"
    CFG.switching_rules = "0:1(%f),1:2(%f),2:0(0.5)" % (p, f)

    return CFG


def cfg_life():
    CFG = CellConfig()
    CFG.possible_states = {0: "Dead", 1: "Alive"}

    CFG.rules = "0:1(3)1,1:1(45678)0,1:0(78)0"

    return CFG


def main():

    CFG = cfg_forest_fire(p=0.1, f=0.001)

    BOARD = Board(CFG, dims=(60, 60), wrap_around=False)
    # BOARD.random_fill(state_back=0, state_front=1, p=0.4)
    # BOARD.random_add(state=2, p=0.5)
    BOARD.fill_edges(state=0)

    BOARD.add_pattern((30, 30), patterns.RPENTOMINO)

    # GPU = CudaSys()
    # GPU.assign_board(BOARD)

    GFX = GraphicSys()
    GFX.assign_board(BOARD)
    BOARD.run(GFX, pause=0.01)


if __name__ == '__main__':
    # cProfile.run('main()', sort='cumtime')
    main()
