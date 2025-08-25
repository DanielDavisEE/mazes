import logging
from enum import IntEnum

import numpy as np

from src.mazes.maze import (
    Direction,
    Maze,
    rng,
)

LOG = logging.getLogger('MazeGeneration')
LOG.setLevel(logging.DEBUG)


class Moves(IntEnum):
    Visit = 0  # Encounter node
    Complete = 1  # Finish processing the node


def _is_visited(maze, node):
    return (maze.maze_array[*node, :] < float('inf')).any()


def recursive_backtrack(maze, current_node=None, *, loop_chance: float = 0.0, move_history: list = None):
    LOG.debug('Creating maze using `recursive_backtrack`')
    if current_node is None:
        current_node = maze.random_node()
    LOG.debug(f'Visiting node: {current_node}')
    if move_history:
        move_history.append((current_node, Moves.Visit))

    directions = np.array(Direction)
    rng.shuffle(directions)
    for direction in directions:
        next_node = maze.move(current_node, direction)
        if next_node in maze.node_set:  # Is it a legal node?
            # Is it an unvisited node, or should we randomly add a loop?
            if not _is_visited(maze, next_node) or rng.random() < loop_chance:
                maze.remove_wall(current_node, direction)
                recursive_backtrack(maze, next_node, move_history=move_history)
    if move_history:
        move_history.append((current_node, Moves.Complete))


def iterative_backtrack(maze: Maze, loop_chance: float = 0.0, move_history: list = None):
    LOG.info('Creating maze using `iterative_backtrack`')
    current_node = maze.random_node()
    move_stack = [current_node]
    directions = np.array(Direction)

    while move_stack:
        LOG.debug(f'Visiting node: {current_node}')
        if move_history:
            move_history.append((current_node, Moves.Visit))

        rng.shuffle(directions)
        for direction in directions:
            next_node = maze.move(current_node, direction)
            if next_node in maze.node_set:  # Is it a legal node?
                # Is it an unvisited node, or should we randomly add a loop?
                if not _is_visited(maze, next_node) or rng.random() < loop_chance:
                    maze.remove_wall(current_node, direction)
                    move_stack.append(current_node)
                    current_node = next_node
                    break
        else:  # Didn't break, backtrack
            current_node = move_stack.pop()
            if move_history:
                move_history.append((current_node, Moves.Complete))
            continue


def ellers(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def kruskals(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def prims(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    LOG.info('Creating maze using `prims`')
    current_node = maze.random_node()
    frontier_set = {(current_node, direction): rng.random() for direction, _ in maze.get_neighbours(current_node)}
    visited_set = {current_node}

    while frontier_set:
        wall = min(frontier_set, key=lambda w: frontier_set[w])
        del frontier_set[wall]

        current_node = maze.move(*wall)
        if current_node in visited_set:
            continue
        LOG.debug(f'Visiting {current_node}')
        maze.remove_wall(*wall)
        visited_set.add(current_node)

        for direction, _ in maze.get_neighbours(current_node):
            frontier_set[(current_node, direction)] = rng.random()


def recursive_divison(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def aldous_broder(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def wilsons(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    # TODO: Fix this, I'm tired
    LOG.info('Creating maze using `wilsons`')
    directions = np.array(Direction)

    walk_root = maze.random_node()
    visited_set = {walk_root}
    LOG.debug(f'Starting at {walk_root}')

    while walk_root in visited_set:
        walk_root = current_node = maze.random_node()
    walk_map = {}

    while len(visited_set) < len(maze.node_set):
        LOG.debug(f'Visiting {current_node}')
        rng.shuffle(directions)
        for direction in directions:
            direction = Direction(direction)
            next_node = maze.move(current_node, direction)
            if next_node in maze.node_set:  # Is it a legal, new node?
                break

        walk_map[current_node] = direction, next_node
        current_node = next_node

        if current_node in visited_set:
            while current_node != walk_root:
                direction, node = walk_map[walk_root]

                maze.remove_wall(walk_root, direction)
                visited_set.add(walk_root)

                walk_root = node

            # TODO: Choose better, at the end all nodes are in visited set
            while walk_root in visited_set:
                walk_root = current_node = maze.random_node()


def hunt_and_kill(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def growing_tree(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def brinary_tree(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


def sidewinder(maze: Maze, *, loop_chance: float = 0.0, move_history: list = None):
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from src.mazes.maze import RectangularMaze
    from src.mazes.maze_views import AsciiView

    maze = RectangularMaze((10, 10))

    wilsons(maze)

    print(AsciiView(maze))
