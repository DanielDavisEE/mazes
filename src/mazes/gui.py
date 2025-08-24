import logging
import tkinter as tk
from tkinter import ttk

from src.mazes.maze import RectangularMaze
from src.mazes.maze_generation import iterative_backtrack
from src.mazes.maze_views import TkRectCanvas
from src.mazes.pathfinding import (a_star, dijkstras, weighted_a_star)

logging.basicConfig(level=logging.DEBUG)

matplotlib_logger = logging.getLogger('matplotlib')
matplotlib_logger.setLevel(logging.INFO)

GENERATION_ALGORITHMS = {
    0: iterative_backtrack,
}

PATHFINDING_ALGORITHMS = {
    0: dijkstras,
    1: a_star,
    2: weighted_a_star,
}


class MazeGui:
    """
    The controller component of the MVC gui model
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

        self.root = tk.Tk()
        self.root.title("Maze GUI")

        self.frame = ttk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.rows_tk = tk.IntVar(value=15, name='RowCount')
        self.cols_tk = tk.IntVar(value=30, name='ColCount')
        self.plot_path = tk.BooleanVar(value=True, name='PlotPath')
        self.visualise_generation = tk.BooleanVar(value=False, name='VisualiseGeneration')

        self.maze = RectangularMaze.blank_maze((self.rows_tk.get(), self.cols_tk.get()))

        self.view = TkRectCanvas(self.frame, self.maze)
        self.view.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ttk.Button(self.button_frame, text='Generate', command=self.generate_custom_maze).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Checkbutton(self.button_frame, text='Show Solution', variable=self.plot_path, command=self.view.toggle_path).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Checkbutton(self.button_frame, text='Visualise Generation', variable=self.visualise_generation).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)

        # Configure window size and placement
        self.root.resizable(True, True)
        self.root.eval('tk::PlaceWindow . center')
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

    def generate_custom_maze(self):
        MAZE_DIMS = self.rows_tk.get(), self.cols_tk.get()

        minimum_path_cost = MAZE_DIMS[0] * MAZE_DIMS[1] * 0.3
        finish_score = 0

        while finish_score < minimum_path_cost:
            maze = RectangularMaze(MAZE_DIMS)
            iterative_backtrack(maze, loop_chance=0.0)

            for _ in range(int(MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1)):
                start = maze.random_node()
                finish = maze.random_node()

                self.log.debug(f"Beginning search at {start}")
                g_scores, path = weighted_a_star(maze, start, finish)
                finish_score = g_scores[finish]

                self.log.debug(f"Reached {finish} with a cost of {finish_score}")
                if finish_score >= minimum_path_cost:
                    break

        self.view.maze = maze
        self.view.start = start
        self.view.finish = finish
        self.view.path = None
        self.view.draw_maze()

        self.view.path = path[1:-1]
        if self.plot_path.get():
            self.view.draw_path()

    def generate_maze(self):
        MAZE_DIMS = self.rows_tk.get(), self.cols_tk.get()

        maze = RectangularMaze(MAZE_DIMS)
        iterative_backtrack(maze)

        start = maze.random_node()
        finish = maze.random_node()

        _g_scores, path = weighted_a_star(maze, start, finish)

        self.view.draw_walls(maze)

        self.view.draw_path(path, delay=0.5)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = MazeGui()
    gui.run()
