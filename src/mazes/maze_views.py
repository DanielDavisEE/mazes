import logging

import numpy as np

from src.mazes.maze import Directions


class ViewBase:
    def __init__(self, maze, start=None, finish=None, path=None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)

        self.maze = maze
        self.start = start
        self.finish = finish
        self.path = path


class AsciiView(ViewBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._maze_array: np.array = None
        self.init_maze_array()

    def __str__(self):
        maze_array = self._maze_array.copy()
        if self.path:
            self.add_path(maze_array)
        if self.start:
            self.add_symbol(maze_array, self.start, 'S')
        if self.finish:
            self.add_symbol(maze_array, self.finish, 'F')

        return '\n'.join(''.join(row) for row in maze_array)

    def add_symbol(self, maze_array, node, symbol):
        row, col = node[0] * 2 + 1, node[1] * 4 + 2
        maze_array[row, col] = symbol
        return row, col

    def _add_move(self, maze_array, node_a, node_b):
        r1, c1 = self.add_symbol(maze_array, node_a, '•')
        r2, c2 = self.add_symbol(maze_array, node_b, '•')

        # Find halfway point of the start and end of the move
        if r1 == r2:
            row = r1
            col = round((c1 + c2) / 2)
        else:
            row = round((r1 + r2) / 2)
            col = c1

        maze_array[row, col] = '•'

    def add_path(self, maze_array):
        for i in range(len(self.path) - 1):
            self._add_move(maze_array, self.path[i], self.path[i + 1])

    def init_maze_array(self):
        maze_array = np.zeros((self.maze.rows * 2 + 1,
                               self.maze.cols * 4 + 1)).astype(object)
        maze_array[:, :] = ' '

        row_coords, col_coords = np.arange(0, maze_array.shape[0], 2), np.arange(0, maze_array.shape[1], 4)

        for i, row_coord in enumerate(row_coords[:-1]):
            maze_array[row_coord, :-1] = np.where(self.maze.maze_array[i, :, Directions.N.value] < float('inf'), ' ' * 4, '-' * 4).view('<U1')
        maze_array[-1, :] = '-'

        for i, col_coord in enumerate(col_coords[:-1]):
            maze_array[:-1, col_coord] = np.where(self.maze.maze_array[:, i, Directions.W.value] < float('inf'), ' ' * 2, '|' * 2).view('<U1')
        maze_array[:, -1] = '|'

        mesh_rows, mesh_cols = np.meshgrid(np.arange(0, maze_array.shape[0], 2), np.arange(0, maze_array.shape[1], 4))
        mesh_rows, mesh_cols = mesh_rows.reshape(-1), mesh_cols.reshape(-1)
        maze_array[mesh_rows, mesh_cols] = '+'
        self._maze_array = maze_array


class TkView(ViewBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
