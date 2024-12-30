import threading
from collections import defaultdict, deque
from heapq import heappop, heappush
import time  # For simulating task duration


### V2
# def execute_tasks_with_robot_exclusion(tasks, dependencies, robot_task_map):
#     # Step 1: Build graph and in-degrees
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0  # Initialize if not already present
#
#     # Step 2: Calculate task levels
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     task_level = {}
#     level = 0
#
#     while queue:
#         size = len(queue)
#         for _ in range(size):
#             current = queue.popleft()
#             task_level[current] = level
#             for neighbor in graph[current]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     queue.append(neighbor)
#         level += 1  # Increment level after processing one level of tasks
#
#     # Group tasks by level for parallel execution
#     level_tasks = defaultdict(list)
#     for task, lvl in task_level.items():
#         level_tasks[lvl].append(task)
#
#     # Step 3: Execute tasks with robot exclusion and availability tracking
#     robot_availability = {robot: 0 for robot in robot_task_map}  # Tracks when each robot is free
#     lock = threading.Lock()  # To ensure thread-safe updates to robot_availability
#
#     def run_task(robot, task):
#         with lock:
#             print(f"Starting task {task} on {robot}")
#         time.sleep(task_durations[task])  # Simulate task duration
#         with lock:
#             print(f"Finished task {task} on {robot}")
#             robot_availability[robot] = time.time()  # Mark robot as free
#
#     for lvl in sorted(level_tasks.keys()):
#         threads = []
#         print(f"Executing level {lvl} tasks in parallel: {level_tasks[lvl]}")
#
#         assigned_robots = set()  # To ensure mutual exclusion for parallel tasks
#         for task in level_tasks[lvl]:
#             while True:
#                 with lock:
#                     current_time = time.time()
#                     available_robots = [robot for robot, free_time in robot_availability.items()
#                                         if free_time <= current_time and task in robot_task_map[
#                                             robot] and robot not in assigned_robots]
#                 if available_robots:
#                     chosen_robot = available_robots[0]  # Pick the first available robot
#                     assigned_robots.add(chosen_robot)
#                     robot_availability[chosen_robot] = current_time + task_durations[task]  # Update availability
#                     thread = threading.Thread(target=run_task, args=(chosen_robot, task))
#                     threads.append(thread)
#                     thread.start()
#                     break
#                 else:
#                     time.sleep(0.1)  # Wait for robots to become available
#         for thread in threads:
#             thread.join()  # Wait for all tasks in the level to complete
#         print(f"Completed all level {lvl} tasks.\n")


def execute_tasks_with_threads(tasks, dependencies, qualified_robot, robots, task_durations):
    # Step 1: Build graph and in-degrees
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for pre, nxt in dependencies:
        graph[pre].append(nxt)
        in_degree[nxt] += 1
        if pre not in in_degree:
            in_degree[pre] = 0  # Initialize if not already present

    # Step 2: Topological sorting to determine task levels
    queue = deque([task for task in in_degree if in_degree[task] == 0])
    task_levels = defaultdict(list)  # Group tasks by levels
    level = 0

    while queue:
        size = len(queue)
        for _ in range(size):
            task = queue.popleft()
            task_levels[level].append(task)
            for neighbor in graph[task]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        level += 1  # Increment level after processing one level of tasks

    # Step 3: Initialize robot availability priority queue
    robot_availability = [(0, robot) for robot in robots]  # (time_free, robot_name)

    def run_task(task, robot, start_time):
        """Function to simulate task execution."""
        print(f"Starting task {task} on {robot} at time {start_time}")
        time.sleep(task_durations[task])  # Simulate task duration
        print(f"Finished task {task} on {robot} at time {start_time + task_durations[task]}")

    # Step 4: Execute tasks level by level
    for lvl, tasks_in_level in task_levels.items():
        print(f"Executing level {lvl} tasks: {tasks_in_level}")

        if len(tasks_in_level) > 1:
            # Parallel execution (multiple tasks in this level)
            threads = []
            for task in tasks_in_level:
                # Find the earliest available robot for this task
                while True:
                    time_free, robot = heappop(robot_availability)  # Get the earliest free robot
                    if robot in [robots[i] for i in qualified_robot[task]]:  # Ensure robot can perform the task
                        break
                    else:
                        heappush(robot_availability, (time_free, robot))  # Put robot back if not qualified

                # Start the task in a thread
                start_time = time_free
                end_time = start_time + task_durations[task]
                thread = threading.Thread(target=run_task, args=(task, robot, start_time))
                threads.append(thread)
                thread.start()

                # Update robot availability
                heappush(robot_availability, (end_time, robot))

            # Wait for all threads in this level to complete
            for thread in threads:
                thread.join()
        else:
            # Sequential execution (only one task in this level)
            task = tasks_in_level[0]
            while True:
                time_free, robot = heappop(robot_availability)  # Get the earliest free robot
                if robot in [robots[i] for i in qualified_robot[task]]:  # Ensure robot can perform the task
                    break
                else:
                    heappush(robot_availability, (time_free, robot))  # Put robot back if not qualified

            # Start the task (no thread needed for sequential tasks)
            start_time = time_free
            end_time = start_time + task_durations[task]
            run_task(task, robot, start_time)
            heappush(robot_availability, (end_time, robot))  # Update robot availability

        print(f"Completed all level {lvl} tasks.\n")


# # Example Input
# tasks = ["1", "2", "3", "4"]  # Task IDs
# dependencies = [("1", "4"), ("2", "3"), ("3", "4")]  # Dependencies
# robots = ["robot_1", "robot_2", "robot_3"]  # Robot names
# qualified_robot = {
#     "1": [0, 1],  # Task 1 can be done by robot_1 and robot_2
#     "2": [0, 1],  # Task 2 can be done by robot_1 and robot_2
#     "3": [1],  # Task 3 can only be done by robot_2
#     "4": [0, 1]  # Task 4 can be done by robot_1 and robot_2
# }
# task_durations = {
#     "1": 2,  # Simulate task 1 takes 2 seconds
#     "2": 3,  # Simulate task 2 takes 3 seconds
#     "3": 2,  # Simulate task 3 takes 2 seconds
#     "4": 1  # Simulate task 4 takes 1 second
# }

tasks = ["1", "2", "3"]
dependencies = [("A", "C"), ("B", "C")]
robots = ["robot_1", "robot_2", "robot_3"]
qualified_robot = {
    "A": [0, 1],  # Task 1 can be done by robot_1 and robot_2
    "B": [0, 1],  # Task 2 can be done by robot_1 and robot_2
    "C": [0, 1],  # Task 3 can only be done by robot_2
}
task_durations = {
    "A": 2,  # Simulate task 1 takes 2 seconds
    "B": 3,  # Simulate task 2 takes 3 seconds
    "C": 2,  # Simulate task 3 takes 2 seconds
}


# Execute tasks
execute_tasks_with_threads(tasks, dependencies, qualified_robot, robots, task_durations)

# # Allocate tasks to robots (preprocessing step)
# def allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots):
#     # Build graph and perform topological sort as in previous implementation
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0
#
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     topo_order = []
#
#     while queue:
#         current = queue.popleft()
#         topo_order.append(current)
#         for neighbor in graph[current]:
#             in_degree[neighbor] -= 1
#             if in_degree[neighbor] == 0:
#                 queue.append(neighbor)
#
#     task_allocation = {}
#
#     def can_assign(robot, task):
#         stack = [task]
#         visited = set()
#         while stack:
#             current = stack.pop()
#             if current in visited:
#                 continue
#             visited.add(current)
#             if robot not in qualified_robot[current]:
#                 return False
#             stack.extend(graph[current])
#         return True
#
#     def assign_task(task, robots):
#         for robot_index in robots:
#             if can_assign(robot_index, task):
#                 task_allocation[task] = robot_index
#                 return True
#         return False
#
#     for task in topo_order:
#         if not assign_task(task, qualified_robot[task]):
#             raise ValueError(f"Task {task} could not be assigned to any robot.")
#
#     robot_task_map = defaultdict(list)
#     for task, robot_index in task_allocation.items():
#         robot_task_map[robots[robot_index]].append(task)
#
#     return robot_task_map
#
#
# robot_task_map = allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots)
#
# # Execute tasks with dynamic robot exclusion
# execute_tasks_with_robot_exclusion(tasks, dependencies, robot_task_map)



### V1
# def execute_tasks_in_parallel(tasks, dependencies, robot_task_map):
#     # Step 1: Build graph and in-degrees
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0  # Initialize if not already present
#
#     # Step 2: Calculate task levels
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     task_level = {}
#     level = 0
#
#     while queue:
#         size = len(queue)
#         for _ in range(size):
#             current = queue.popleft()
#             task_level[current] = level
#             for neighbor in graph[current]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     queue.append(neighbor)
#         level += 1  # Increment level after processing one level of tasks
#
#     # Group tasks by level for parallel execution
#     level_tasks = defaultdict(list)
#     for task, lvl in task_level.items():
#         level_tasks[lvl].append(task)
#
#     # Step 3: Execute tasks using threads
#     def run_task(task):
#         robot = next(robot for robot, tasks in robot_task_map.items() if task in tasks)
#         print(f"Starting task {task} on {robot}")
#         time.sleep(task_durations[task])  # Simulate task duration
#         print(f"Finished task {task} on {robot}")
#
#     for lvl in sorted(level_tasks.keys()):
#         threads = []
#         print(f"Executing level {lvl} tasks in parallel: {level_tasks[lvl]}")
#         for task in level_tasks[lvl]:
#             thread = threading.Thread(target=run_task, args=(task,))
#             threads.append(thread)
#             thread.start()
#         for thread in threads:
#             thread.join()  # Wait for all tasks in the level to complete
#         print(f"Completed all level {lvl} tasks.\n")
#
#
# # Example Input
# # tasks = ["1", "2", "3", "4"]  # Task IDs
# # dependencies = [("A", "D"), ("B", "C"), ("C", "D")]  # Dependencies
# # robots = ["robot_1", "robot_2", "robot_3"]  # Robot names
# # qualified_robot = {
# #     "A": [0, 1],  # Task 1 can be done by robot_1 and robot_2
# #     "B": [0, 1],  # Task 2 can be done by robot_1 and robot_2
# #     "C": [1],  # Task 3 can only be done by robot_2
# #     "D": [0, 1]  # Task 4 can be done by robot_1 and robot_2
# # }
# # task_durations = {
# #     "A": 2,  # Simulate task 1 takes 2 seconds
# #     "B": 3,  # Simulate task 2 takes 3 seconds
# #     "C": 2,  # Simulate task 3 takes 2 seconds
# #     "D": 1  # Simulate task 4 takes 1 second
# # }
#
# tasks = ["1", "2", "3"]
# dependencies = [("A", "C"), ("B", "C")]
# robots = ["robot_1", "robot_2", "robot_3"]
# qualified_robot = {
#     "A": [0, 1],  # Task 1 can be done by robot_1 and robot_2
#     "B": [0, 1],  # Task 2 can be done by robot_1 and robot_2
#     "C": [0, 1],  # Task 3 can only be done by robot_2
# }
# task_durations = {
#     "A": 2,  # Simulate task 1 takes 2 seconds
#     "B": 3,  # Simulate task 2 takes 3 seconds
#     "C": 2,  # Simulate task 3 takes 2 seconds
# }
#
#
# # Step 1: Allocate tasks to robots
# def allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots):
#     # Build graph and perform topological sort as in previous implementation
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0
#
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     topo_order = []
#
#     while queue:
#         current = queue.popleft()
#         topo_order.append(current)
#         for neighbor in graph[current]:
#             in_degree[neighbor] -= 1
#             if in_degree[neighbor] == 0:
#                 queue.append(neighbor)
#
#     task_allocation = {}
#
#     def can_assign(robot, task):
#         stack = [task]
#         visited = set()
#         while stack:
#             current = stack.pop()
#             if current in visited:
#                 continue
#             visited.add(current)
#             if robot not in qualified_robot[current]:
#                 return False
#             stack.extend(graph[current])
#         return True
#
#     def assign_task(task, robots):
#         for robot_index in robots:
#             if can_assign(robot_index, task):
#                 task_allocation[task] = robot_index
#                 return True
#         return False
#
#     for task in topo_order:
#         if not assign_task(task, qualified_robot[task]):
#             raise ValueError(f"Task {task} could not be assigned to any robot.")
#
#     robot_task_map = defaultdict(list)
#     for task, robot_index in task_allocation.items():
#         robot_task_map[robots[robot_index]].append(task)
#
#     return robot_task_map
#
#
# robot_task_map = allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots)
#
# # Step 2: Execute tasks in parallel
# execute_tasks_in_parallel(tasks, dependencies, robot_task_map)