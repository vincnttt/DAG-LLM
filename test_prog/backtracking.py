from collections import defaultdict, deque


def allocate_task_dependencies(tasks, dependencies, qualified_robots, robots):
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for prev, next in dependencies:
        graph[prev].append(next)
        in_degree[next] += 1
        if prev not in in_degree:
            in_degree[prev] = 0

    queue = deque([task for task in in_degree if in_degree[task] == 0])
    topo_order = []

    while queue:
        curr = queue.popleft()
        topo_order.append(curr)
        for neighbor in graph[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(topo_order) != len(in_degree):
        raise ValueError("Task dependency cycle detected")

    task_allocation = {}

    def can_assign(robot, task):
        stack = [task]
        visited = set()
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            if robot not in qualified_robots[curr]:
                return False
            stack.extend(graph[curr])
        return True

    def assign_task(task, robots):
        for robot_index in robots:
            if can_assign(robot_index, task):
                task_allocation[task] = robot_index
                return True
        return False

    for task in topo_order:
        if not assign_task(task, qualified_robots[task]):
            raise ValueError(f"Task {task} could not be assigned to any robot")

    robot_task_map = defaultdict(list)
    for task, robot_index in task_allocation.items():
        robot_task_map[robots[robot_index]].append(task)

    return robot_task_map


if __name__ == "__main__":
    # tasks = ["1", "2", "3", "4"]
    # dependencies = [("1", "4"), ("2", "3"), ("3", "4")]
    # robots = ["robot_1", "robot_2", "robot_3"]
    # qualified_robot = {
    #     "1": [0, 1],  # Task 1 can be done by robot_1 and robot_2
    #     "2": [0, 1],  # Task 2 can be done by robot_1 and robot_2
    #     "3": [1],  # Task 3 can only be done by robot_2
    #     "4": [0, 1]  # Task 4 can be done by robot_1 and robot_2
    # }

    tasks = ["A", "B", "C", "D"]
    dependencies = [("A", "D"), ("B", "C"), ("C", "D")]
    robots = ["robot_1", "robot_2", "robot_3"]
    qualified_robot = {
        "A": [0, 1],  # Task 1 can be done by robot_1 and robot_2
        "B": [0, 1],  # Task 2 can be done by robot_1 and robot_2
        "C": [1],  # Task 3 can only be done by robot_2
        "D": [0, 1]  # Task 4 can be done by robot_1 and robot_2
    }

    allocation = allocate_task_dependencies(tasks, dependencies, qualified_robot, robots)

    # print(allocation)
    for robot, task in allocation.items():
        print(f"{robot}: Task {task}")