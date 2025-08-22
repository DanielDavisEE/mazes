import logging
import tkinter as tk

from src.mazes.maze import RectangularMaze
from src.mazes.maze_generation import iterative_backtrack
from src.mazes.pathfinding import weighted_a_star
from src.mazes.maze_views import TkRectView

logging.basicConfig(level=logging.DEBUG)

matplotlib_logger = logging.getLogger('matplotlib')
matplotlib_logger.setLevel(logging.INFO)


class MazeGui:
    """
    The controller component of the MVC gui model
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

        self.root = tk.Tk()
        self.root.title("Maze GUI")

        self.view = TkRectView(self.root)

        # Configure window size and placement
        self.root.resizable(True, True)
        self.root.eval('tk::PlaceWindow . center')
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

    def init_maze(self):
        MAZE_DIMS = (10, 20)

        minimum_path_cost = MAZE_DIMS[0] * MAZE_DIMS[1] * 0.3
        finish_score = 0

        while finish_score < minimum_path_cost:
            maze = RectangularMaze(MAZE_DIMS)
            iterative_backtrack(maze)

            for _ in range(int(MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1)):
                start = maze.random_node()
                for finish, _ in maze.get_neighbours(start):

                    self.log.info(f"Beginning search at {start}")
                    g_scores, path = weighted_a_star(maze, start, finish)
                    finish_score = g_scores[finish]

                    self.log.info(f"Reached {finish} with a cost of {finish_score}")
                    if finish_score >= minimum_path_cost:
                        break
                if finish_score >= minimum_path_cost:
                    break

        self.view.maze = maze
        self.view.start = start
        self.view.finish = finish
        self.view.path = path

        self.draw_path()

        view = TkRectView(maze, start, finish, path)
        view.run()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = MazeGui()
    gui.run()
