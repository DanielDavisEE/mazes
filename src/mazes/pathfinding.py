import logging
from collections import deque

from src.mazes.maze import (
    Maze,
    Node,
)

LOG = logging.getLogger('PathFinding')
LOG.setLevel('INFO')


def reconstruct_path(move_map, goal) -> list:
    node = goal

    path = [node]
    while (node := move_map[node]) is not None:
        path.append(node)

    return list(reversed(path))


def dijkstras_mapper(maze: Maze, start: Node) -> tuple[dict, dict]:
    """ Dijkstra's implementation that maps the entire graph in relation to the start node.

    Args:
        maze: The maze to be mapped
        start: The starting node

    Returns:
        A dictionary of the G_score for every node on the map
        A dictionary of the previous node in the optimal path to the start
    """
    frontier_set = {start}

    move_map = {start: None}
    g_score = {}
    g_score[start] = 0

    while frontier_set:
        current_node = min(frontier_set, key=lambda n: g_score[n])
        frontier_set.remove(current_node)

        for direction, node in maze.get_neighbours(current_node):
            cost = maze.edge_cost(current_node, direction)
            if g_score[current_node] + cost < g_score.get(node, float('inf')):
                frontier_set.add(node)
                g_score[node] = g_score[current_node] + cost
                move_map[node] = current_node

    return g_score, move_map


def dijkstras(maze: Maze, start: Node, finish: Node, *, move_history: list = None) -> tuple[dict, list[Node]]:
    return weighted_a_star(maze, start, finish, weight=0, move_history=move_history)


def a_star(maze: Maze, start: Node, finish: Node, *, move_history: list = None) -> tuple[dict, list[Node]]:
    return weighted_a_star(maze, start, finish, weight=1, move_history=move_history)


def weighted_a_star(maze: Maze, start: Node, finish: Node, *, weight: float = 2.0, move_history: list = None) -> tuple[dict, list[Node]]:
    frontier_set = {start}

    move_map = {start: None}
    g_score = {start: 0}
    f_score = {start: maze.find_distance(start, finish) * weight}

    while frontier_set:
        # Possibility for optimisation here by using a heap/priority queue instead of a set ( O(n) -> O(log(n)) )
        current_node = min(frontier_set, key=lambda n: f_score[n])
        if current_node == finish:
            return g_score, reconstruct_path(move_map, finish)

        frontier_set.remove(current_node)

        for direction, node in maze.get_neighbours(current_node):
            possible_g_score = g_score[current_node] + maze.edge_cost(current_node, direction)
            if possible_g_score < g_score.get(node, float('inf')):
                g_score[node] = possible_g_score
                f_score[node] = possible_g_score + maze.find_distance(node, finish) * weight
                move_map[node] = current_node

                # This is only relevant if a node is reached a second time with a lower score, as might happen
                #  if the heuristic function (find_distance) is not consistent
                if node not in frontier_set:
                    frontier_set.add(node)

    raise RuntimeError(f"Could not find path from {start} to {finish}: {move_map}")


def breadth_first_search(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    frontier_queue = deque([start])

    move_map = {start: None}
    g_score = {start: 0}

    while frontier_queue:
        current_node = frontier_queue.popleft()
        if current_node == finish:
            return g_score, reconstruct_path(move_map, finish)

        for direction, node in maze.get_neighbours(current_node):
            possible_g_score = g_score[current_node] + maze.edge_cost(current_node, direction)
            if possible_g_score < g_score.get(node, float('inf')):
                g_score[node] = possible_g_score
                move_map[node] = current_node

                if node not in frontier_queue:
                    frontier_queue.append(node)

    raise RuntimeError(f"Could not find path from {start} to {finish}")


def _dfs_recurse(maze: Maze, current_node: Node, finish: Node, g_score: dict, move_map: dict):
    if current_node == finish:
        return

    for direction, node in maze.get_neighbours(current_node):
        if node in move_map or maze.edge_cost(current_node, direction) == float('inf'):
            continue
        move_map[node] = current_node
        g_score[node] = g_score[current_node] + maze.edge_cost(current_node, direction)
        if _dfs_recurse(maze, node, finish, g_score, move_map):
            return


def depth_first_search_recursive(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    g_score = {start: 0}
    move_map = {start: None}
    _dfs_recurse(maze, start, finish, g_score, move_map)
    if finish not in g_score:
        raise RuntimeError(f"Could not find path from {start} to {finish}")
    path = reconstruct_path(move_map, finish)
    return g_score, path


def depth_first_search_iterative(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    frontier_stack = [start]

    move_map = {start: None}
    g_score = {start: 0}

    while frontier_stack:
        current_node = frontier_stack.pop()
        if current_node == finish:
            return g_score, reconstruct_path(move_map, finish)

        for direction, node in maze.get_neighbours(current_node):
            possible_g_score = g_score[current_node] + maze.edge_cost(current_node, direction)
            if possible_g_score < g_score.get(node, float('inf')):
                g_score[node] = possible_g_score
                move_map[node] = current_node

                if node not in frontier_stack:
                    frontier_stack.append(node)

    raise RuntimeError(f"Could not find path from {start} to {finish}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    from src.mazes.maze import RectangularMaze
    from src.mazes.maze_views import (
        AsciiView,
        TkView,
    )
    from src.mazes.maze_generation import wilsons as maze_maker

    maze_solver = depth_first_search_recursive

    MAZE_DIMS = (20, 40)

    minimum_path_cost = MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1
    finish_score = 0
    maze_count = 0
    solve_count = 0

    while finish_score < minimum_path_cost:
        maze = RectangularMaze(MAZE_DIMS)
        maze_maker(maze)
        maze_count += 1

        for _ in range(int(MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1)):
            solve_count += 1
            start = maze.random_node()
            for _, finish in maze.get_neighbours(start):

                LOG.debug(f"Beginning search at {start}")
                g_scores, path = maze_solver(maze, start, finish)
                finish_score = g_scores[finish]

                LOG.debug(f"Reached {finish} with a cost of {finish_score}")
                if finish_score >= minimum_path_cost:
                    break
            if finish_score >= minimum_path_cost:
                break

    LOG.info(f"Attempted {solve_count} solves on {maze_count} mazes")
    AsciiView(maze, start, finish, path)
    TkView(maze, start, finish, path)
