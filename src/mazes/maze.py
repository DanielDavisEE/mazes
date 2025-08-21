import logging
from enum import IntEnum

import numpy as np

rng = np.random.default_rng()


class Directions(IntEnum):
    N = 0
    W = 1
    S = 2
    E = 3

    def flip(self):
        return Directions((self.value + 2) % 4)


DIRECTION_OPS = {
    Directions.N: np.array([-1, 0]),
    Directions.W: np.array([0, -1]),
    Directions.S: np.array([1, 0]),
    Directions.E: np.array([0, 1]),
}

Node = tuple[int, int]

class Maze:
    pass

class RectangularMaze(Maze):
    def __init__(self, dimensions: tuple[int, int]):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)

        self.rows = dimensions[0]
        self.cols = dimensions[1]

        self.maze_array = np.ones((*dimensions, 4)) * float('inf')
        # self.maze_array = np.random.random((*dimensions, 4)) > 0.5

        self.node_set: set[Node] = set([(i, j) for i in range(self.rows) for j in range(self.cols)])

    def move(self, node: Node, direction: Directions) -> Node:
        row, col = np.array(node) + DIRECTION_OPS[direction]
        return int(row), int(col)

    def edge_cost(self, node: Node, direction: Directions) -> float:
        return self.maze_array[*node, direction.value]

    def is_wall(self, node: Node, direction: Directions):
        return self.edge_cost(node, direction) == float('inf')

    def remove_wall(self, node: Node, direction: Directions) -> None:
        if isinstance(direction, (int, np.int64)):
            direction = Directions(direction)
        self.maze_array[*node, direction.value] = 1

        dest_node = self.move(node, direction)
        if all(coord >= 0 for coord in dest_node):
            self.maze_array[*dest_node, direction.flip().value] = 1

    def get_neighbours(self, node: Node) -> list[tuple[Node, float]]:
        possible_nodes = [(self.move(node, direction), float(self.edge_cost(node, direction))) for direction in Directions]
        return [(node, cost) for node, cost in possible_nodes if node in self.node_set]

    def random_node(self) -> Node:
        row, col = tuple(rng.integers((self.rows, self.cols), size=2))
        return int(row), int(col)

    def find_distance(self, node_a: Node, node_b: Node):
        if node_a not in self.node_set or node_b not in self.node_set:
            self.log.warning(f'Invalid node input: {node_a}, {node_b}')
        return np.abs(np.array(node_a) - np.array(node_b)).sum()
