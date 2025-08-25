import logging
from abc import (
    ABC,
    abstractmethod,
)
from enum import Enum

import numpy as np

rng = np.random.default_rng()


class Direction(Enum):
    N = 0
    W = 1
    S = 2
    E = 3

    def flip(self):
        return Direction((self.value + 2) % 4)


DIRECTION_OPS = {
    Direction.N: np.array([-1, 0]),
    Direction.W: np.array([0, -1]),
    Direction.S: np.array([1, 0]),
    Direction.E: np.array([0, 1]),
}

Node = tuple[int, int]


class Maze(ABC):
    node_set: set

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)

    @abstractmethod
    def move(self, node: Node, direction: Direction) -> Node:
        raise NotImplementedError

    @abstractmethod
    def edge_cost(self, node: Node, direction: Direction) -> float:
        raise NotImplementedError

    @abstractmethod
    def is_wall(self, node: Node, direction: Direction) -> bool:
        raise NotImplementedError

    @abstractmethod
    def remove_wall(self, node: Node, direction: Direction):
        raise NotImplementedError

    @abstractmethod
    def get_neighbours(self, node: Node) -> list[tuple[Direction, Node]]:
        raise NotImplementedError

    @abstractmethod
    def random_node(self) -> Node:
        raise NotImplementedError

    @abstractmethod
    def find_distance(self, node_a: Node, node_b: Node) -> float:
        raise NotImplementedError


class RectangularMaze(Maze):
    def __init__(self, dimensions: tuple[int, int], generation_alg=None):
        super().__init__()

        self.rows = dimensions[0]
        self.cols = dimensions[1]

        self.maze_array = np.ones((*dimensions, 4)) * float('inf')
        self.node_set: set[Node] = set([(i, j) for i in range(self.rows) for j in range(self.cols)])

        if generation_alg:
            generation_alg(self)

    @classmethod
    def blank_maze(cls, dimensions):
        inst = cls(dimensions)
        inst.maze_array = np.zeros((*dimensions, 4))
        return inst

    def move(self, node: Node, direction: Direction) -> Node:
        row, col = np.array(node) + DIRECTION_OPS[direction]
        return int(row), int(col)

    def edge_cost(self, node: Node, direction: Direction) -> float:
        return self.maze_array[*node, direction.value]

    def is_wall(self, node: Node, direction: Direction) -> bool:
        return self.edge_cost(node, direction) == float('inf')

    def remove_wall(self, node: Node, direction: Direction):
        if isinstance(direction, (int, np.int64)):
            direction = Direction(direction)
        self.maze_array[*node, direction.value] = 1

        dest_node = self.move(node, direction)
        if all(coord >= 0 for coord in dest_node):
            self.maze_array[*dest_node, direction.flip().value] = 1

    def get_neighbours(self, node: Node) -> list[tuple[Direction, Node]]:
        possible_nodes = [(direction, self.move(node, direction)) for direction in Direction]
        return [(direction, node) for direction, node in possible_nodes if node in self.node_set]

    def random_node(self) -> Node:
        row, col = tuple(rng.integers((self.rows, self.cols), size=2))
        return int(row), int(col)

    def find_distance(self, node_a: Node, node_b: Node) -> float:
        if node_a not in self.node_set or node_b not in self.node_set:
            self.log.warning(f'Invalid node input: {node_a}, {node_b}')
        return np.abs(np.array(node_a) - np.array(node_b)).sum()
