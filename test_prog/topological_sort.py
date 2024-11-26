from collections import deque, defaultdict


def allocate_tasks(dag, task_steps, num_robots):
    """
    Allocate subtasks in a DAG to multiple robots using topological sorting.
    :param dag: Dictionary representing the DAG {node: [dependent nodes]}
    :param task_steps: Dictionary mapping each node to its step count
    :param num_robots: Number of robots available
    :return: Allocation plan {robot_id: [task_list]}
    """
    # Step 1: Calculate in-degrees for topological sorting
    in_degree = {node: 0 for node in dag}
    for node in dag:
        for dependent in dag[node]:
            in_degree[dependent] += 1

    # Step 2: Perform topological sorting (Kahn's Algorithm)
    topo_sort = []
    queue = deque([node for node in dag if in_degree[node] == 0])

    while queue:
        current = queue.popleft()
        topo_sort.append(current)
        for neighbor in dag[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Step 3: Allocate tasks to robots
    robot_load = [0] * num_robots  # Track workload (steps) for each robot
    allocation = defaultdict(list)  # Track task assignments per robot

    for task in topo_sort:
        # Assign task to the robot with the least workload
        robot_id = robot_load.index(min(robot_load))
        allocation[robot_id].append(task)
        robot_load[robot_id] += task_steps[task]

    return allocation


# Example usage
if __name__ == "__main__":
    # Define the DAG
    dag = {
        1: [3],  # Subtask 1 -> Subtask 3
        2: [4],  # Subtask 3 -> Subtask 4
        3: [4],  # Subtask 4 -> Subtask 2
        4: []  # Subtask 4 has no dependencies
    }

    # Define steps required for each subtask
    task_steps = {
        1: 12,  # Subtask 1: wash plate
        2: 10,  # Subtask 2: wash vegetable
        3: 10,  # Subtask 3: slice vegetable
        4: 16  # Subtask 4: serve sliced vegetable on plate
    }

    # Number of robots
    num_robots = 2

    # Allocate tasks
    allocation = allocate_tasks(dag, task_steps, num_robots)
    print("Task allocation to robots:", dict(allocation))

