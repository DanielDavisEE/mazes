import logging
from enum import IntEnum

import numpy as np

from src.mazes.maze import Directions, Maze, rng

LOG = logging.getLogger('MazeGeneration')
logging.basicConfig(level='INFO')
LOG.setLevel('INFO')


class Moves(IntEnum):
    Visit = 0  # Encounter node
    Complete = 1  # Finish processing the node


def recursive_backtrack(maze, current_node=None, loop_chance: float = 0.0, *, move_history: list = None):
    LOG.debug('Creating maze using `recursive_backtrack`')
    if current_node is None:
        current_node = maze.random_node()
    LOG.debug(f'Visiting node: {current_node}')
    if move_history:
        move_history.append((current_node, Moves.Visit))

    directions = np.array(Directions)
    rng.shuffle(directions)
    for direction in directions:
        next_node = maze.move(current_node, direction)
        if next_node in maze.node_set:  # Is it a legal node?
            # Is it an unvisited node, or should we randomly add a loop?
            if (maze.maze_array[*next_node, :] == float('inf')).all() or rng.random() < loop_chance:
                maze.remove_wall(current_node, direction)
                recursive_backtrack(maze, next_node, move_history=move_history)
    if move_history:
        move_history.append((current_node, Moves.Complete))


def iterative_backtrack(maze: Maze, loop_chance: float = 0.0, *, move_history: list = None):
    LOG.info('Creating maze using `iterative_backtrack`')
    current_node = maze.random_node()
    move_stack = [current_node]
    directions = np.array(Directions)

    while move_stack:
        LOG.debug(f'Visiting node: {current_node}')
        if move_history:
            move_history.append((current_node, Moves.Visit))

        rng.shuffle(directions)
        for direction in directions:
            next_node = maze.move(current_node, direction)
            if next_node in maze.node_set:  # Is it a legal node?
                # Is it an unvisited node, or should we randomly add a loop?
                if (maze.maze_array[*next_node, :] == float('inf')).all() or rng.random() < loop_chance:
                    maze.remove_wall(current_node, direction)
                    move_stack.append(current_node)
                    current_node = next_node
                    break
        else:  # Didn't break, backtrack
            current_node = move_stack.pop()
            if move_history:
                move_history.append((current_node, Moves.Complete))
            continue


def ellers(maze: Maze):
    pass


def kruskals(maze: Maze):
    pass


def prims(maze: Maze):
    pass


def recursive(maze: Maze):
    pass


def aldous_broder(maze: Maze):
    pass


def wilsons(maze: Maze):
    pass


def hunt_and_kill(maze: Maze):
    pass


def growing_tree(maze: Maze):
    pass


def brinary_tree(maze: Maze):
    pass


def sidewinder(maze: Maze):
    pass


if __name__ == '__main__':
    from src.mazes.maze import RectangularMaze
    from src.mazes.maze_views import AsciiView

    maze = RectangularMaze((10, 10))

    recursive_backtrack(maze)

    print(AsciiView(maze))
