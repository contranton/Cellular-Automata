import pygame as pg
import colorsys

from time import sleep


class GraphicSys:
    def __init__(self, dims=(400, 400)):

        self.win_w, self.win_h = dims

        # For use with pygame
        self._display = None

        self.board = None
        self.colors = {}

    def assign_board(self, board):
        self.board = board

        # Conversion scales to draw grid
        self.cell_x_size = self.win_w/board.w
        self.cell_y_size = self.win_h/board.h

        # Set up the colors
        _states = self.board.config.possible_states
        _n_states = len(_states)
        self.colors[0] = (0, 0, 0)
        for state in _states[1:]:
            col = colorsys.hsv_to_rgb((state - 1)/_n_states, 1, 1)
            col = [_*255 for _ in col]
            self.colors[state] = col

        print("COLORS ASSIGNED: %s" % str(self.colors))

    def draw_board(self):
        """
        Outputs the assigned board to the display
        """

        self._display.fill((50, 50, 50))

        if self.board is None:
            print("Must assign a board first")
            return

        for cell in self.board.iter_cells():
            _state = cell.current_state
            pg.draw.rect(self._display,
                         self.colors[_state],
                         (self.cell_x_size*cell.coords[0],
                          self.cell_y_size*cell.coords[1],
                          self.cell_x_size,
                          self.cell_y_size
                          ))
        pg.display.flip()

    def initialize(self):
        """Start the window and set graphical parameters"""
        pg.init()
        self._display = pg.display.set_mode((self.win_w, self.win_h))

    def close(self):
        pg.quit()

    def check_input(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return False
        return True
