import logging
import tkinter as tk
from tkinter import ttk

from src.mazes.maze import RectangularMaze
from src.mazes.maze_generation import (
    aldous_broder,
    brinary_tree,
    ellers,
    growing_tree,
    hunt_and_kill,
    iterative_backtrack,
    kruskals,
    prims,
    recursive_backtrack,
    recursive_divison,
    sidewinder,
    wilsons,
)
from src.mazes.maze_views import (
    AsciiView,
    TkRectCanvas,
)
from src.mazes.pathfinding import (
    a_star,
    breadth_first_search,
    depth_first_search_iterative,
    depth_first_search_recursive,
    dijkstras,
    weighted_a_star,
)

GENERATION_ALGORITHMS = {
    'Iterative Backtrack': iterative_backtrack,
    'Recursive Backtrack': recursive_backtrack,
    "Ellers x": ellers,
    "Kruskal's x": kruskals,
    "Prim's": prims,
    'Recursive Divison x': recursive_divison,
    'Aldous-Broder x': aldous_broder,
    "Wilson's": wilsons,
    'Hunt and Kill x': hunt_and_kill,
    'Growing Tree x': growing_tree,
    'Binary Tree x': brinary_tree,
    'Sidewinder x': sidewinder,
}

PATHFINDING_ALGORITHMS = {
    "Dijkstra's": dijkstras,
    "A*": a_star,
    "Weighted A*": weighted_a_star,
    "Breadth First Search": breadth_first_search,
    "Depth First Search (Recursive)": depth_first_search_recursive,
    "Depth First Search (Iterative)": depth_first_search_iterative,
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
        self.plot_path_tk = tk.BooleanVar(value=True, name='PlotPath')
        self.visualise_generation_tk = tk.BooleanVar(value=False, name='VisualiseGeneration')
        self.generation_algorithm_tk = tk.StringVar(value='Iterative Backtrack', name='GenerationAlgorithm')
        self.pathfinding_algorithm_tk = tk.StringVar(value='A*', name='PathfindingAlgorithm')

        self.maze = RectangularMaze.blank_maze((self.rows_tk.get(), self.cols_tk.get()))

        self.view = TkRectCanvas(self.frame, self.maze)
        self.view.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.options_frame = ttk.Frame(self.frame)
        self.options_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ttk.Button(self.options_frame, text='Generate', command=self.generate_custom_maze).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Checkbutton(self.options_frame, text='Show Solution', variable=self.plot_path_tk, command=self.view.toggle_path).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Checkbutton(self.options_frame, text='Visualise Generation', variable=self.visualise_generation_tk).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Combobox(self.options_frame, textvariable=self.generation_algorithm_tk, values=list(GENERATION_ALGORITHMS.keys())).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Combobox(self.options_frame, textvariable=self.pathfinding_algorithm_tk, values=list(PATHFINDING_ALGORITHMS.keys())).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)

        # Configure window size and placement
        self.root.resizable(True, True)
        self.root.eval('tk::PlaceWindow . center')
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

    @property
    def generation_algorithm(self):
        return GENERATION_ALGORITHMS[self.generation_algorithm_tk.get()]

    @property
    def pathfinding_algorithm(self):
        return PATHFINDING_ALGORITHMS[self.pathfinding_algorithm_tk.get()]

    def generate_custom_maze(self):
        MAZE_DIMS = self.rows_tk.get(), self.cols_tk.get()

        minimum_path_cost = MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1
        finish_score = 0

        while finish_score < minimum_path_cost:
            maze = RectangularMaze(MAZE_DIMS)
            self.generation_algorithm(maze, loop_chance=0.0)

            for _ in range(int(MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1)):
                start = maze.random_node()
                finish = maze.random_node()

                self.log.debug(f"Beginning search at {start}")
                try:
                    g_scores, path = a_star(maze, start, finish)
                except:
                    AsciiView(maze, start, finish)
                    raise
                finish_score = g_scores[finish]

                self.log.debug(f"Reached {finish} with a cost of {finish_score}")
                if finish_score >= minimum_path_cost:
                    break

        self.view.maze = maze
        self.view.start = start
        self.view.finish = finish
        self.view.path = None
        self.view.draw_maze()

        _g_score, path = self.pathfinding_algorithm(maze, start, finish)
        self.view.path = path[1:-1]
        if self.plot_path_tk.get():
            self.view.draw_path()

    def generate_maze(self):
        MAZE_DIMS = self.rows_tk.get(), self.cols_tk.get()

        maze = RectangularMaze(MAZE_DIMS)
        iterative_backtrack(maze)

        start = maze.random_node()
        finish = maze.random_node()

        _g_scores, path = weighted_a_star(maze, start, finish)

        self.view.draw_walls(maze)

        self.view.draw_path(path)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    gui = MazeGui()
    gui.run()
