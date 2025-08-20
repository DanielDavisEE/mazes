import logging

from src.mazes.maze import Maze, Node

LOG = logging.getLogger('PathFinding')
logging.basicConfig(level='INFO')
LOG.setLevel('INFO')


def reconstruct_path(move_map, goal) -> list:
    node = goal

    path = [node]
    while (node := move_map[node]) is not None:
        path.append(node)

    return list(reversed(path))


def dijkstras(maze: Maze, start: Node, finish: Node = None):
    frontier_set = {start}

    move_map = {node: None for node in maze.node_set}
    g_score = {node: float('inf') for node in maze.node_set}
    g_score[start] = 0

    while frontier_set:
        current_code = min(frontier_set, key=lambda n: g_score[n])
        frontier_set.remove(current_code)

        if finish and current_code == finish:
            break

        for node, cost in maze.get_neighbours(current_code):
            if g_score[current_code] + cost < g_score[node]:
                frontier_set.add(node)
                g_score[node] = g_score[current_code] + cost
                move_map[node] = current_code

    return g_score, move_map


def a_star(maze: Maze):
    pass


def weighted_a_star(maze: Maze, weight):
    pass


def breadth_first_search(maze: Maze):
    pass


def depth_first_search(maze: Maze):
    pass


if __name__ == '__main__':
    from src.mazes.maze import AcsiiView
    from src.mazes.maze_generation import iterative_backtrack as maze_maker
    maze_solver = dijkstras

    maze = Maze((11, 11))
    maze_maker(maze)
    start = (0, 5)  # maze.random_node()
    maze.remove_wall(start, 'N')

    LOG.info(f"Beginning search at {start}")
    g_scores, move_map = maze_solver(maze, start)

    finish = max(g_scores, key=lambda n: g_scores[n])
    LOG.info(f"Reached {finish} with a cost of {g_scores[finish]}")
    print(AcsiiView(maze, start, finish, reconstruct_path(move_map, finish)))
