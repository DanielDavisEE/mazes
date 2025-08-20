import logging

import numpy as np

LOG = logging.getLogger('MazeClass')
logging.basicConfig(level='INFO')
LOG.setLevel('INFO')

rng = np.random.default_rng()

DIRECTIONS = {
    'N': np.array([-1, 0]),
    'W': np.array([0, -1]),
    'S': np.array([1, 0]),
    'E': np.array([0, 1]),
}

Node = tuple[int, int]


class Maze:
    def __init__(self, dimensions: tuple[int, int]):
        self.rows = dimensions[0]
        self.cols = dimensions[1]

        self.maze_array = np.ones((*dimensions, 4)) * float('inf')
        # self.maze_array = np.random.random((*dimensions, 4)) > 0.5

        self.direction_layer_map = {
            'N': 0,
            'W': 1,
            'S': 2,
            'E': 3,
        }

        self.node_set: set[Node] = set([(i, j) for i in range(self.rows) for j in range(self.cols)])

    def move(self, node: Node, direction: str) -> Node:
        row, col = np.array(node) + DIRECTIONS[direction]
        return int(row), int(col)

    def edge_cost(self, node: Node, direction: str) -> float:
        return self.maze_array[*node, self.direction_layer_map[direction]]

    def is_wall(self, node: Node, direction: str):
        return self.edge_cost(node, direction) == float('inf')

    def remove_wall(self, node: Node, direction: str) -> None:
        dest_node = self.move(node, direction)

        layer = self.direction_layer_map[direction]
        reverse_layer = (layer + 2) % 4

        self.maze_array[*node, layer] = 1

        if all(coord >= 0 for coord in dest_node):
            self.maze_array[*dest_node, reverse_layer] = 1

    def get_neighbours(self, node: Node) -> list[tuple[Node, float]]:
        possible_nodes = [(self.move(node, direction), float(self.edge_cost(node, direction))) for direction in DIRECTIONS]
        return [(node, cost) for node, cost in possible_nodes if node in self.node_set]

    def random_node(self) -> Node:
        row, col = tuple(rng.integers((self.rows, self.cols), size=2))
        return int(row), int(col)

    def find_distance(self, node_a: Node, node_b: Node):
        if node_a not in self.node_set or node_b not in self.node_set:
            LOG.warning(f'Invalid node input: {node_a}, {node_b}')
        return np.abs(np.array(node_a) - np.array(node_b)).sum()


class AcsiiView:
    def __init__(self, maze, start=None, finish=None, path=None):
        self.maze = maze
        self.start = start
        self.finish = finish
        self.path = path

        self._maze_string_width = self.maze.cols * 4 + 2
        self.clean_maze_string = self._to_string()
        self.maze_string = None

    def __str__(self):
        self.maze_string = self.clean_maze_string[:]
        if self.path:
            self.add_path()
        if self.start:
            self.add_symbol(self.start, 'S')
        if self.finish:
            self.add_symbol(self.finish, 'F')
        return self.maze_string

    def add_symbol(self, node, symbol):
        row, col = node[0] * 2 + 1, node[1] * 4 + 2
        self.maze_string = (self.maze_string[:self._maze_string_width * row + col]
                            + symbol
                            + self.maze_string[self._maze_string_width * row + col + 1:])
        return row, col

    def _add_move(self, node_a, node_b):
        r1, c1 = self.add_symbol(node_a, '•')
        r2, c2 = self.add_symbol(node_b, '•')

        # Find halfway point of the start and end of the move
        if r1 == r2:
            row = r1
            col = round((c1 + c2) / 2)
        else:
            row = round((r1 + r2) / 2)
            col = c1

        self.maze_string = (self.maze_string[:self._maze_string_width * row + col]
                            + '•'
                            + self.maze_string[self._maze_string_width * row + col + 1:])


    def add_path(self):
        for i in range(len(self.path) - 1):
            self._add_move(self.path[i], self.path[i + 1])

    def _to_string(self) -> str:
        """
        puts " " + "_" * (width * 2 - 1)
        height.times do |y|
          print "|"
          width.times do |x|
            print((grid[y][x] & S != 0) ? " " : "_")
            if grid[y][x] & E != 0
              print(((grid[y][x] | grid[y][x+1]) & S != 0) ? " " : "_")
            else
              print "|"
            end
          end
          puts
        end
        """
        maze_string = ''
        for i in range(self.maze.rows):
            maze_string += '+' + '+'.join('---' if self.maze.is_wall((i, j), 'N') else '   ' for j in range(self.maze.cols)) + '+\n'
            maze_string += ''.join('|   ' if self.maze.is_wall((i, j), 'W') else '    ' for j in range(self.maze.cols)) + ('|' if self.maze.is_wall((i, self.maze.cols - 1), 'E') else ' ') + '\n'
        maze_string += '+' + '+'.join('---' if self.maze.is_wall((self.maze.rows - 1, j), 'S') else '   ' for j in range(self.maze.cols)) + '+'
        return maze_string
