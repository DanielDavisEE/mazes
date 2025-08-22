import logging
import tkinter as tk
from tkinter import ttk

import numpy as np

from src.mazes.maze import Directions, Maze, RectangularMaze


class ViewBase:
    def __init__(self, maze=None, start=None, finish=None, path=None):
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


class TkRectView(ViewBase):
    SQUARE_PX = 41
    LINE_WIDTH = 2
    MARGIN = 10

    _maze = None

    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = ttk.Frame(master)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_canvas(self):
        self.canvas.delete("all")

        self.width_px = self.maze.cols * (self.SQUARE_PX + self.LINE_WIDTH) + self.LINE_WIDTH + 2 * self.MARGIN
        self.height_px = self.maze.rows * (self.SQUARE_PX + self.LINE_WIDTH) + self.LINE_WIDTH + 2 * self.MARGIN

        self.canvas = tk.Canvas(self.frame, width=self.width_px, height=self.height_px, background='gray90')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        if self.maze:
            self.draw_walls()
            if self.path:
                self.draw_path()

    @property
    def maze(self) -> RectangularMaze:
        return self._maze

    @maze.setter
    def maze(self, maze: RectangularMaze):
        if maze is None:
            return
        self._maze = maze
        self.draw_walls()

    def rc_to_xy(self, node, align=tk.NW):
        square_offset = (self.SQUARE_PX + self.LINE_WIDTH)
        x, y = (node[1] * square_offset + self.MARGIN,
                node[0] * square_offset + self.MARGIN)
        match align:
            # Sides
            case tk.N:
                x += square_offset // 2
            case tk.S:
                x += square_offset // 2
                y += square_offset
            case tk.W:
                y += square_offset // 2
            case tk.E:
                x += square_offset
                y += square_offset // 2

            # Corners
            case tk.NW:
                pass
            case tk.SW:
                y += square_offset
            case tk.NE:
                x += square_offset
            case tk.SE:
                x += square_offset
                y += square_offset

            # Centre
            case tk.NS | tk.EW | tk.NSEW | tk.CENTER:
                x += square_offset // 2
                y += square_offset // 2

            case _:
                raise RuntimeError(f"{align=}")
        return x, y

    def _draw_wall(self, node, direction):
        match direction:
            case Directions.N:
                line_origin = node
                line_dest = self.maze.move(node, Directions.E)
            case Directions.W:
                line_origin = node
                line_dest = self.maze.move(node, Directions.S)
            case Directions.S:
                line_origin = self.maze.move(node, Directions.S)
                line_dest = self.maze.move(self.maze.move(node, Directions.E), Directions.S)
            case Directions.E:
                line_origin = self.maze.move(node, Directions.E)
                line_dest = self.maze.move(self.maze.move(node, Directions.E), Directions.S)
            case _:
                raise RuntimeError(f"{direction=}")
        line_origin_px = self.rc_to_xy(line_origin, align=tk.NW)
        line_dest_px = self.rc_to_xy(line_dest, align=tk.NW)

        self.canvas.create_line(*line_origin_px, *line_dest_px, width=self.LINE_WIDTH)

    def draw_walls(self):
        for i in range(self.maze.rows):
            for j in range(self.maze.cols):
                if self.maze.is_wall((i, j), Directions.N):
                    self._draw_wall((i, j), Directions.N)
                if self.maze.is_wall((i, j), Directions.W):
                    self._draw_wall((i, j), Directions.W)
        for i in range(self.maze.rows):
            if self.maze.is_wall((i, self.maze.cols - 1), Directions.E):
                self._draw_wall((i, self.maze.cols - 1), Directions.E)
        for j in range(self.maze.cols):
            if self.maze.is_wall((self.maze.rows - 1, j), Directions.S):
                self._draw_wall((self.maze.rows - 1, j), Directions.S)

    def draw_path(self):
        for i in range(len(self.path) - 1):
            start, stop = self.path[i], self.path[i + 1]
            start_px = self.rc_to_xy(start, align=tk.CENTER)
            stop_px = self.rc_to_xy(stop, align=tk.CENTER)
            self.canvas.create_line(*start_px, *stop_px, width=self.LINE_WIDTH, dash=(2, 2))
