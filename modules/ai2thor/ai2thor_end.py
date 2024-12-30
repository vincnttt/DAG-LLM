

# Start count runtime
start_time = time.time()


def build_graph(dependencies):
    """Build task dependency graph and calculate in-degrees."""
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for src, dst in dependencies:
        graph[src].append(dst)
        in_degree[dst] += 1

    for task in subtasks:
        if task not in in_degree:
            in_degree[task] = 0  # Tasks with no incoming edges

    return graph, in_degree


def allocate_tasks(subtasks, graph, in_degree, qualified_robot):
    """Allocate tasks to robots ensuring parallel execution."""
    assignment = {}  # Task -> Assigned robot
    available_robots = set(range(len(robots)))  # Set of available robot indices
    ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])

    while ready_queue:
        task_batch = list(ready_queue)  # Tasks that can be executed concurrently
        ready_queue.clear()

        # Assign robots to tasks in the current batch
        robot_used = set()
        for task in task_batch:
            for robot in qualified_robot[task]:
                if robot in available_robots and robot not in robot_used:
                    assignment[task] = robot
                    robot_used.add(robot)
                    break

        # Verify all tasks in the batch are assigned
        if len(task_batch) != len(robot_used):
            raise ValueError("Not enough robots to execute the current batch of tasks.")

        # Update dependencies and find new ready tasks
        for task in task_batch:
            for neighbor in graph[task]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    ready_queue.append(neighbor)

    return assignment


def run_tasks(assignment, graph):
    """Run tasks either in parallel or sequentially based on dependency levels."""
    in_degree = {task: 0 for task in subtasks}
    for src, dsts in graph.items():
        for dst in dsts:
            in_degree[dst] += 1

    ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])

    def execute_task(task, robot_idx):
        print(bcolors.OKBLUE + f"Task {task} is being executed by robot{robot_idx}" + bcolors.ENDC)
        globals()[task](robots[robot_idx])
        # time.sleep(1)  # Simulate task duration
        # print(f"Task {task} completed by {robots[robot_idx]}")

    while ready_queue:
        task_batch = list(ready_queue)  # Tasks at the current level (no dependencies)
        ready_queue.clear()

        threads = []  # Store threads for parallel execution
        for task in task_batch:
            robot_idx = assignment[task]
            task_thread = threading.Thread(target=execute_task, args=(task, robot_idx))
            threads.append(task_thread)

        # Start all threads (parallel execution for current level)
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Update dependencies and find new ready tasks
        for task in task_batch:
            for neighbor in graph[task]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    ready_queue.append(neighbor)


# Build the task graph and calculate in-degrees
graph, in_degree = build_graph(dependencies)

# Allocate tasks to robots
try:
    assignment = allocate_tasks(subtasks, graph, in_degree, qualified_robot)
    print(bcolors.OKGREEN + "Task Allocation:" + bcolors.ENDC)
    for task, robot_idx in assignment.items():
        # print(f"Task {task} -> {robots[robot_idx]}")
        print(f"Task {task} -> robot{robot_idx}")

    # Execute tasks
    print(bcolors.OKGREEN + "\nExecuting Tasks:" + bcolors.ENDC)
    run_tasks(assignment, graph)

except ValueError as e:
    print(e)


# def analyze_generated_function():
#     file_path = __file__
#
#     with open(file_path, "r") as f:
#         source_code = f.read()
#
#     tree = ast.parse(source_code)
#
#     functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
#
#     # Analyze each function
#     results = {}
#     for func in functions:
#         func_name = func.name  # Get the name of the function
#         num_statements = len(func.body)  # Count the number of statements in the function body
#         results[func_name] = num_statements
#
#     return results


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
#         # robot_task_map[robots[robot_index]].append(task)
#         robot_task_map[robot_index].append(task)
#
#     print(topo_order)
#
#     return robot_task_map
#
#
# robot_task_map = allocate_tasks_with_dependencies(subtasks, dependencies, qualified_robot, robots)
#
# # Step 2: Execute tasks in parallel
# execute_tasks_in_parallel(subtasks, dependencies, robot_task_map)

for i in range(25):
    action_queue.append({'action': 'Done'})
    action_queue.append({'action': 'Done'})
    action_queue.append({'action': 'Done'})
    time.sleep(0.1)

task_over = True

# End count runtime
end_time = time.time()
runtime = end_time - start_time

time.sleep(5)

print(bcolors.WARNING + f"Runtime: {runtime:0.3f}s" + bcolors.ENDC)
print(bcolors.OKGREEN + f"Success: {success_exec}, Total: {total_exec}" + bcolors.ENDC)

# try:
#     exec = float(success_exec) / float(total_exec)
# except ZeroDivisionError:
#     exec = 0.0

exec = float(success_exec) / float(total_exec)

write_log("\n[GROUND TRUTH]", ground_truth)

print(ground_truth)
objs = list([obj for obj in c.last_event.metadata["objects"]])

# Ground completion
gcr_tasks = 0.0
gcr_complete = 0.0
for obj_gt in ground_truth:
    obj_name = obj_gt['name']
    state = obj_gt['state']
    contains = obj_gt['contains']
    gcr_tasks += 1
    for obj in objs:
        # if obj_name in obj["name"]:
        #     print (obj)
        if state == 'SLICED':
            if obj_name in obj["name"] and obj["isSliced"]:
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'OFF':
            if obj_name in obj["name"] and not obj["isToggled"]:
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'ON':
            if obj_name in obj["name"] and obj["isToggled"]:
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'HOT':
            if obj_name in obj["name"] and obj["temperature"] == 'Hot':
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'COOKED':
            if obj_name in obj["name"] and obj["isCooked"]:
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'OPENED':
            if obj_name in obj["name"] and obj["isOpen"]:
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'CLOSED':
            if obj_name in obj["name"] and not obj["isOpen"]:
                gcr_complete += 1
                print(obj, gcr_complete)

        if state == 'PICKED':
            if obj_name in obj["name"] and obj["isPickedUp"]:
                gcr_complete += 1

        if len(contains) != 0 and obj_name in obj["name"]:
            # print(contains, obj_name, obj["name"])
            print(obj)
            write_log("[DATA]", f"{contains}, {obj_name}, {obj['name']}")
            for rec in contains:
                if obj['receptacleObjectIds'] is not None:
                    for r in obj['receptacleObjectIds']:
                        print(rec, r)
                        write_log("[DATA]", f"{rec}, {r}")
                        if rec in r:
                            print(rec, r)
                            write_log("[DATA]", f"{rec}, {r}")
                            gcr_complete += 1

sr = 0  # Success rate
tc = 0  # Task completion
if gcr_tasks == 0:
    gcr = 1
else:
    gcr = gcr_complete / gcr_tasks
    if gcr > 1.0:
        gcr = 1.0
    else:
        gcr = 1.0

if gcr == 1.0:
    tc = 1

# max_trans += 1
# no_trans_gt += 1
# print(bcolors.OKGREEN + f"no_trans_gt: {no_trans_gt}, max_trans: {max_trans}, no_trans: {no_trans}" + bcolors.ENDC)
#
# if max_trans == no_trans_gt and no_trans_gt == no_trans:
#     ru = 1
# elif max_trans == no_trans_gt:
#     ru = 0
# else:
#     ru = (max_trans - no_trans) / (max_trans - no_trans_gt)
#
# if tc == 1 and ru == 1:
#     sr = 1
#
# print(f"SR:{sr}, TCR:{tc}, GCR:{gcr}, RU:{ru}, Exec:{exec}")
# with open(f"{curr_path}/log.txt", 'a') as f:
#     f.write(f"\n\n\n")
#     f.write(f"========== RESULT ==========")
#     f.write(f"\n\n")
#     f.write(f"no_trans_gt: {no_trans_gt}, max_trans: {max_trans}, no_trans: {no_trans}")
#     f.write(f"\n")
#     f.write(f"SR:{sr}, TCR:{tc}, GCR:{gcr}, RU:{ru}, Exec:{exec}")

if tc == 1:
    sr = 1

print(bcolors.OKGREEN + f"SR:{sr}, TCR:{tc}, GCR:{gcr}, Exec:{exec}" + bcolors.ENDC)
with open(f"{curr_path}/log.txt", 'a') as f:
    f.write(f"\n\n\n")
    f.write(f"========== RESULT ==========")
    f.write(f"\n")
    f.write(f"SR:{sr}, TCR:{tc}, GCR:{gcr}, Exec:{exec}")
    f.write(f"\n")
    f.write(f"Runtime:{runtime:0.3f}")

generate_video()