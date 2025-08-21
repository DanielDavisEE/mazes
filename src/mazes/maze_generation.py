import logging

import numpy as np

from src.mazes.maze import Directions, RectangularMaze, rng

LOG = logging.getLogger('MazeGeneration')
logging.basicConfig(level='INFO')
LOG.setLevel('INFO')


def recursive_backtrack(maze, current_node=None, loop_chance: float = 0.0):
    LOG.debug('Creating maze using `recursive_backtrack`')
    if current_node is None:
        current_node = maze.random_node()
    LOG.debug(f'Visiting node: {current_node}')

    directions = np.array(Directions)
    rng.shuffle(directions)
    for direction in directions:
        next_node = maze.move(current_node, direction)
        if next_node in maze.node_set:  # Is it a legal node?
            # Is it an unvisited node, or should we randomly add a loop?
            if (maze.maze_array[*next_node, :] == float('inf')).all() or rng.random() < loop_chance:
                maze.remove_wall(current_node, direction)
                recursive_backtrack(maze, next_node)


def iterative_backtrack(maze: RectangularMaze, loop_chance: float = 0.0):
    LOG.info('Creating maze using `iterative_backtrack`')
    current_node = maze.random_node()
    move_stack = [current_node]
    directions = np.array(Directions)

    while move_stack:
        LOG.debug(f'Visiting node: {current_node}')

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
            continue


def ellers(maze: RectangularMaze):
    pass


def kruskals(maze: RectangularMaze):
    pass


def prims(maze: RectangularMaze):
    pass


def recursive(maze: RectangularMaze):
    pass


def aldous_broder(maze: RectangularMaze):
    pass


def wilsons(maze: RectangularMaze):
    pass


def hunt_and_kill(maze: RectangularMaze):
    pass


def growing_tree(maze: RectangularMaze):
    pass


def brinary_tree(maze: RectangularMaze):
    pass


def sidewinder(maze: RectangularMaze):
    pass


if __name__ == '__main__':
    maze = RectangularMaze((10, 10))

    recursive_backtrack(maze)

    print(maze.to_string())
