import logging

from src.mazes.maze import Node, Maze

LOG = logging.getLogger('PathFinding')
logging.basicConfig(level='INFO')
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

    move_map = {node: None for node in maze.node_set}
    g_score = {node: float('inf') for node in maze.node_set}
    g_score[start] = 0

    while frontier_set:
        current_code = min(frontier_set, key=lambda n: g_score[n])
        frontier_set.remove(current_code)

        for node, cost in maze.get_neighbours(current_code):
            if g_score[current_code] + cost < g_score[node]:
                frontier_set.add(node)
                g_score[node] = g_score[current_code] + cost
                move_map[node] = current_code

    return g_score, move_map


def dijkstras(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    return weighted_a_star(maze, start, finish, weight=0)


def a_star(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    return weighted_a_star(maze, start, finish, weight=1)


def weighted_a_star(maze: Maze, start: Node, finish: Node, *, weight: float = 2.0) -> tuple[dict, list[Node]]:
    frontier_set = {start}

    move_map = {node: None for node in maze.node_set}

    g_score = {node: float('inf') for node in maze.node_set}
    g_score[start] = 0

    f_score = {node: float('inf') for node in maze.node_set}
    f_score[start] = maze.find_distance(start, finish) * weight

    while frontier_set:
        # Possibility for optimisation here by using a heap/priority queue instead of a set ( O(n) -> O(log(n)) )
        current_code = min(frontier_set, key=lambda n: f_score[n])
        if current_code == finish:
            return g_score, reconstruct_path(move_map, finish)

        frontier_set.remove(current_code)

        for node, cost in maze.get_neighbours(current_code):
            possible_g_score = g_score[current_code] + cost
            if possible_g_score < g_score[node]:
                frontier_set.add(node)
                g_score[node] = possible_g_score
                f_score[node] = possible_g_score + maze.find_distance(node, finish) * weight
                move_map[node] = current_code

                # This is only relevant if a node is reached a second time with a lower score, as might happen
                #  if the heuristic function (find_distance) is not consistent
                if node not in frontier_set:
                    frontier_set.add(node)

    raise RuntimeError(f"Could not find path from {start} to {finish}")


def breadth_first_search(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    pass


def depth_first_search(maze: Maze, start: Node, finish: Node) -> tuple[dict, list[Node]]:
    pass


if __name__ == '__main__':
    from src.mazes.maze import RectangularMaze
    from src.mazes.maze_views import TkRectView
    from src.mazes.maze_generation import iterative_backtrack as maze_maker

    maze_solver = weighted_a_star

    MAZE_DIMS = (10, 20)

    minimum_path_cost = MAZE_DIMS[0] * MAZE_DIMS[1] * 0.3
    finish_score = 0

    while finish_score < minimum_path_cost:
        maze = RectangularMaze(MAZE_DIMS)
        maze_maker(maze)

        for _ in range(int(MAZE_DIMS[0] * MAZE_DIMS[1] * 0.1)):
            start = maze.random_node()
            for finish, _ in maze.get_neighbours(start):

                LOG.info(f"Beginning search at {start}")
                g_scores, path = maze_solver(maze, start, finish)
                finish_score = g_scores[finish]

                LOG.info(f"Reached {finish} with a cost of {finish_score}")
                if finish_score >= minimum_path_cost:
                    break
            if finish_score >= minimum_path_cost:
                break

    view = TkRectView(maze, start, finish, path)
    view.run()
