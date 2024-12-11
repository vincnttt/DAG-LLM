import threading
from collections import defaultdict, deque
import time  # For simulating task duration


def execute_tasks_in_parallel(tasks, dependencies, robot_task_map):
    # Step 1: Build graph and in-degrees
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for pre, nxt in dependencies:
        graph[pre].append(nxt)
        in_degree[nxt] += 1
        if pre not in in_degree:
            in_degree[pre] = 0  # Initialize if not already present

    # Step 2: Calculate task levels
    queue = deque([task for task in in_degree if in_degree[task] == 0])
    task_level = {}
    level = 0

    while queue:
        size = len(queue)
        for _ in range(size):
            current = queue.popleft()
            task_level[current] = level
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        level += 1  # Increment level after processing one level of tasks

    # Group tasks by level for parallel execution
    level_tasks = defaultdict(list)
    for task, lvl in task_level.items():
        level_tasks[lvl].append(task)

    # Step 3: Execute tasks using threads
    def run_task(task):
        robot = next(robot for robot, tasks in robot_task_map.items() if task in tasks)
        print(f"Starting task {task} on {robot}")
        time.sleep(task_durations[task])  # Simulate task duration
        print(f"Finished task {task} on {robot}")

    for lvl in sorted(level_tasks.keys()):
        threads = []
        print(f"Executing level {lvl} tasks in parallel: {level_tasks[lvl]}")
        for task in level_tasks[lvl]:
            thread = threading.Thread(target=run_task, args=(task,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()  # Wait for all tasks in the level to complete
        print(f"Completed all level {lvl} tasks.\n")


# Example Input
tasks = ["1", "2", "3", "4"]  # Task IDs
dependencies = [("A", "D"), ("B", "C"), ("C", "D")]  # Dependencies
robots = ["robot_1", "robot_2", "robot_3"]  # Robot names
qualified_robot = {
    "A": [0, 1],  # Task 1 can be done by robot_1 and robot_2
    "B": [0, 1],  # Task 2 can be done by robot_1 and robot_2
    "C": [1],  # Task 3 can only be done by robot_2
    "D": [0, 1]  # Task 4 can be done by robot_1 and robot_2
}
task_durations = {
    "A": 2,  # Simulate task 1 takes 2 seconds
    "B": 3,  # Simulate task 2 takes 3 seconds
    "C": 2,  # Simulate task 3 takes 2 seconds
    "D": 1  # Simulate task 4 takes 1 second
}


# Step 1: Allocate tasks to robots
def allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots):
    # Build graph and perform topological sort as in previous implementation
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for pre, nxt in dependencies:
        graph[pre].append(nxt)
        in_degree[nxt] += 1
        if pre not in in_degree:
            in_degree[pre] = 0

    queue = deque([task for task in in_degree if in_degree[task] == 0])
    topo_order = []

    while queue:
        current = queue.popleft()
        topo_order.append(current)
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    task_allocation = {}

    def can_assign(robot, task):
        stack = [task]
        visited = set()
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            if robot not in qualified_robot[current]:
                return False
            stack.extend(graph[current])
        return True

    def assign_task(task, robots):
        for robot_index in robots:
            if can_assign(robot_index, task):
                task_allocation[task] = robot_index
                return True
        return False

    for task in topo_order:
        if not assign_task(task, qualified_robot[task]):
            raise ValueError(f"Task {task} could not be assigned to any robot.")

    robot_task_map = defaultdict(list)
    for task, robot_index in task_allocation.items():
        robot_task_map[robots[robot_index]].append(task)

    return robot_task_map


robot_task_map = allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots)

# Step 2: Execute tasks in parallel
execute_tasks_in_parallel(tasks, dependencies, robot_task_map)