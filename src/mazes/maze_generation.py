import logging

import numpy as np

LOG = logging.getLogger('MazeGeneration')
logging.basicConfig(level='INFO')
LOG.setLevel('INFO')

rng = np.random.default_rng()

DIRECTIONS = {
    'N': np.array([-1, 0]),
    'W': np.array([0, -1]),
    'S': np.array([1, 0]),
    'E': np.array([0, 1]),
}


class Maze:
    def __init__(self, dimensions: tuple[int, int]):
        self.rows = dimensions[0]
        self.cols = dimensions[1]

        self.maze_array = np.ones((*dimensions, 4))
        # self.maze_array = np.random.random((*dimensions, 4)) > 0.5

        self.direction_layer_map = {
            'N': 0,
            'W': 1,
            'S': 2,
            'E': 3,
        }

        self.node_set = set([(i, j) for i in range(self.rows) for j in range(self.cols)])

    def move(self, node, direction):
        return tuple(np.array(node) + DIRECTIONS[direction])

    def remove_wall(self, node: tuple[int, int], direction: str) -> None:
        dest_node = self.move(node, direction)

        layer = self.direction_layer_map[direction]
        reverse_layer = (layer + 2) % 4

        self.maze_array[*node, layer] = 0
        self.maze_array[*dest_node, reverse_layer] = 0

    def is_wall(self, node, direction):
        return self.maze_array[*node, self.direction_layer_map[direction]]

    def to_string(self) -> str:
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
        for i in range(self.rows):
            maze_string += '+' + '+'.join('---' if self.is_wall((i, j), 'N') else '   ' for j in range(self.cols)) + '+\n'
            maze_string += ''.join('|   ' if self.is_wall((i, j), 'W') else '    ' for j in range(self.cols)) + ('|' if self.is_wall((i, self.cols - 1), 'E') else ' ') + '\n'
        maze_string += '+' + '+'.join('---' if self.is_wall((self.rows - 1, j), 'S') else '   ' for j in range(self.cols)) + '+'
        return maze_string


def recursive_backtrack(maze, current_node=None, loop_chance: float = 0.02):
    LOG.debug('Creating maze using `recursive_backtrack`')
    if current_node is None:
        current_node = tuple(rng.integers((maze.rows, maze.cols), size=2))
    LOG.debug(f'Visiting node: {current_node}')

    directions = np.array(list(DIRECTIONS.keys()))
    rng.shuffle(directions)
    for direction in directions:
        next_node = maze.move(current_node, direction)
        if next_node in maze.node_set:  # Is it a legal node?
            # Is it an unvisited node, or should we randomly add a loop?
            if maze.maze_array[*next_node, :].all() or rng.random() < loop_chance:
                maze.remove_wall(current_node, direction)
                recursive_backtrack(maze, next_node)


def iterative_backtrack(maze: Maze, loop_chance: float = 0.02):
    LOG.info('Creating maze using `iterative_backtrack`')
    current_node = tuple(rng.integers((maze.rows, maze.cols), size=2))
    move_stack = [current_node]
    directions = np.array(list(DIRECTIONS.keys()))

    while move_stack:
        LOG.debug(f'Visiting node: {current_node}')

        rng.shuffle(directions)
        for direction in directions:
            next_node = maze.move(current_node, direction)
            if next_node in maze.node_set:  # Is it a legal node?
                # Is it an unvisited node, or should we randomly add a loop?
                if maze.maze_array[*next_node, :].all() or rng.random() < loop_chance:
                    maze.remove_wall(current_node, direction)
                    move_stack.append(current_node)
                    current_node = next_node
                    break
        else:  # Didn't break, backtrack
            current_node = move_stack.pop()
            continue


if __name__ == '__main__':
    maze = Maze((10, 10))

    recursive_backtrack(maze)

    print(maze.to_string())
