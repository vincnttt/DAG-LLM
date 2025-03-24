

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


def assign_tasks_dynamically(graph, in_degree, independent_tasks, qualified_robot):
    """Dynamically assign tasks to robots while respecting dependencies."""
    # Queue of ready tasks (tasks with in-degree 0)
    ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])

    # Queue for independent tasks
    independent_queue = deque(independent_tasks)

    # Track completed tasks
    completed_tasks = set()

    # Robot availability tracking
    robot_status = {i: True for i in range(len(robots))}  # True means available
    robot_locks = {i: threading.Lock() for i in range(len(robots))}
    task_assignment_lock = threading.Lock()  # Synchronize task assignment

    # Task execution function
    def execute_task(task, robot_idx):
        with robot_locks[robot_idx]:
            # Mark robot as busy
            robot_status[robot_idx] = False
            # print(f"Task '{task}' is being executed by {robot_idx}")
            # time.sleep(1)  # Simulate task duration
            # print(f"Task '{task}' completed by {robot_idx}")
            with open(f"{curr_path}/log.txt", 'a') as f:
                f.write(f"\nTask {task} is being executed by robot{robot_idx}\n")
            print(bcolors.OKBLUE + f"Task {task} is being executed by robot{robot_idx}" + bcolors.ENDC)
            globals()[task](robots[robot_idx])
            # Mark robot as available and task as completed
            robot_status[robot_idx] = True
            completed_tasks.add(task)

    # Dynamic task assignment
    threads = []
    while ready_queue or independent_queue:
        # Synchronize task assignment
        with task_assignment_lock:
            # Process dependent tasks first
            task_batch = list(ready_queue)
            ready_queue.clear()

            for task in task_batch:
                if task in completed_tasks:  # Skip already completed tasks
                    continue
                assigned = False
                for robot_idx, available in robot_status.items():
                    if available and robot_idx in qualified_robot[task]:
                        thread = threading.Thread(target=execute_task, args=(task, robot_idx))
                        threads.append(thread)
                        thread.start()
                        assigned = True
                        break
                if not assigned:
                    ready_queue.append(task)  # Re-enqueue if no robot available

            # Process independent tasks if robots are available
            independent_batch = list(independent_queue)
            independent_queue.clear()

            for task in independent_batch:
                if task in completed_tasks:  # Skip already completed tasks
                    continue
                assigned = False
                for robot_idx, available in robot_status.items():
                    if available and robot_idx in qualified_robot[task]:
                        thread = threading.Thread(target=execute_task, args=(task, robot_idx))
                        threads.append(thread)
                        thread.start()
                        assigned = True
                        break
                if not assigned:
                    independent_queue.append(task)  # Re-enqueue if no robot available

        # Wait for threads to finish
        for thread in threads:
            thread.join()

        # Update dependencies for dependent tasks
        for task in task_batch:
            for neighbor in graph[task]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0 and neighbor not in completed_tasks:
                    ready_queue.append(neighbor)


# Build the task graph and calculate in-degrees
graph, in_degree = build_graph(dependencies)

# Separate dependent and independent tasks
dependent_tasks = set(graph.keys()).union(*graph.values())
independent_tasks = set(subtasks) - dependent_tasks

# Assign tasks dynamically
print(bcolors.OKGREEN + "\nExecuting Tasks:" + bcolors.ENDC)
assign_tasks_dynamically(graph, in_degree, independent_tasks, qualified_robot)

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
            if obj_name in obj["name"] and obj["temperature"] == 'RoomTemp':
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
    if gcr < 1.0:
        gcr = gcr
    else:
        gcr = 1.0

if gcr == 1.0 and exec == 1.0:
    sr = 1
else:
    sr = 0

print(bcolors.OKGREEN + f"SR:{sr}, GCR:{gcr}, Exec:{exec}" + bcolors.ENDC)
with open(f"{curr_path}/log.txt", 'a') as f:
    f.write(f"\n\n\n")
    f.write(f"========== RESULT ==========")
    f.write(f"\n")
    f.write(f"SR:{sr}, GCR:{gcr}, Exec:{exec}")
    f.write(f"\n")
    f.write(f"Runtime:{runtime:0.3f}")

generate_video()