from src.mazes.maze import Maze, Node, RectangularMaze


class MazeAgent:
    def __init__(self):
        self.known_maze: Maze = RectangularMaze((1, 1))
        self.known_position: Node = 0, 0

    def turn(self):
        pass

    def drive(self):
        pass
