from time import sleep
from collections import defaultdict
from random import random

from cell import Cell


class Board:
    """Defines a board with multiple cells inside"""

    def __init__(self, config, dims=(40, 40), wrap_around=False):

        self.set_config(config)

        # Physical parameters
        self.w, self.h = dims[0], dims[1]
        self.wrap_around = wrap_around

        # Initialize empty cells
        # Dict of the form {coordinate: CellObject)
        self.cells = {}
        for i in range(self.w):
            for j in range(self.h):
                self.cells[(i, j)] = Cell(state=self.states[0], coords=(i, j))

        # Mark edges
        for i in range(self.w):
            self.cells[(i, 0)].is_edge = True
            self.cells[(i, self.h - 1)].is_edge = True

        for j in range(self.h):
            self.cells[(0, j)].is_edge = True
            self.cells[(self.w - 1, j)].is_edge = True

    def __str__(self):
        s = ""
        for i in range(self.w):
            for j in range(self.h):
                s += str(self.cells[(i, j)].current_state)  # MAKE THIS A JOIN
            s += "\n"
        return s

    def iter_cells(self):
        for i in range(self.w):
            for j in range(self.h):
                yield self.cells[(i, j)]

    def set_config(self, config):
        # Cell state and rule settings
        self.config = config
        self.states = config.possible_states  # For convenience

    def copy_board(self):
        """Generates a copy of the current board and all its cells"""
        new_board = Board(self.config, (self.w, self.h), self.wrap_around)
        for cell in new_board.iter_cells():
            cell.current_state = self.cells[cell.coords].current_state
        return new_board

    def replace_board(self, other_board):
        """Replaces all of this board's cells with the other_board's cells"""
        for cell in self.iter_cells():
            cell.current_state = other_board.cells[cell.coords].current_state

    def fill(self, state):
        """Fill every cell on board with given state"""
        for cell in self.iter_cells():
            cell.current_state = state

    def random_fill(self, state_back, state_front, p):
        """Fill the board randomly (uniform p) with the given state"""
        self.fill(state=state_back)
        for cell in self.iter_cells():
            if random() < p:
                cell.current_state = state_front

    def random_add(self, state, p):
        for cell in self.iter_cells():
            if random() < p:
                cell.current_state = state

    def fill_edges(self, state):
        for cell in self.iter_cells():
            if cell.is_edge:
                cell.current_state = state

    def add_pattern(self, coords, pattern):
        for j, row in enumerate(pattern.split(",")):
            for i, state in enumerate((int(s) for s in row.strip())):
                try:
                    self.cells[(coords[0]+i, coords[1]+j)
                               ].current_state = state
                except IndexError:
                    raise Exception("Pattern out of bounds")

    def update(self):
        """Apply config-rules to update cell states"""
        new_board = self.copy_board()

        for coord, cell in self.cells.items():
            if cell.is_edge:
                continue

            # Get neighbor rules
            try:
                rules = self.config.rules[cell.current_state]

                # Get cell neighbor information
                for neigh_state, count in self.acquire_neighbor_info(coord).items():
                    # Check if neighbor rule can be applied
                    if neigh_state in rules and count in rules[neigh_state][0]:
                        # Apply the rule
                        new_board.cells[coord].current_state = rules[neigh_state][1]

            except KeyError:
                pass

            # Get switching rule if it exists
            try:
                sw_rule = self.config.switching_rules[cell.current_state]

                if random() < sw_rule[1]:
                    new_board.cells[coord].current_state = sw_rule[0]

            except KeyError:
                continue

        self.replace_board(new_board)

    def acquire_neighbor_info(self, coord):
        i, j = coord
        neighs = (self.cells[i-1, j-1],
                  self.cells[i, j-1],
                  self.cells[i+1, j-1],
                  self.cells[i-1, j],
                  self.cells[i+1, j],
                  self.cells[i-1, j+1],
                  self.cells[i, j+1],
                  self.cells[i+1, j+1])
        neighs = (i.current_state for i in neighs)

        cell = self.cells[coord]
        cell.reset_neighbors()
        for i in neighs:
            cell.neighbors[i] += 1
        return cell.neighbors

    def run(self, graphics, pause=0):
        """Simulation loop. Check for events and updates cells"""
        graphics.initialize()
        print(self.config.rules)

        step = 0
        while True:
            if not graphics.check_input():
                graphics.close()
                print("Generations run: %i" % step)
                break
            graphics.draw_board()
            self.update()
            sleep(pause)

            step += 1
