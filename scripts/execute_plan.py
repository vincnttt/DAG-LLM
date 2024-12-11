import os
import ast
import subprocess
import argparse

from pathlib import Path
from collections import deque, defaultdict


def append_trans_ctr(allocated_plan):
    brk_ctr = 0
    code_segs = allocated_plan.split("\n\n")
    fn_calls = []
    for cd in code_segs:
        if "def" not in cd and "threading.Thread" not in cd and "join" not in cd and cd[-1] == ")":
            # fn_calls.append(cd)
            brk_ctr += 1
    print("No Breaks: ", brk_ctr)
    return brk_ctr


def analyze_python_file(file_path):
    # Read the contents of the file
    with open(file_path, "r") as f:
        source_code = f.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Find all function definitions in the file
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    # Analyze each function
    results = {}
    for func in functions:
        func_name = func.name  # Get the name of the function
        num_statements = len(func.body)  # Count the number of statements in the function body
        results[func_name] = num_statements

    return results


def allocate_tasks(dag, task_steps, num_robots):
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


def compile_aithor_exec_file(expt_name):
    log_path = os.getcwd() + "/outputs/" + expt_name
    executable_plan = ""

    # append the imports to the file
    import_file = Path(os.getcwd() + "/modules/ai2thor/ai2thor_start.py").read_text()
    executable_plan += (import_file + "\n")

    # append the list of robots and floor plan number
    log_file = open(log_path + "/log.txt")
    log_data = log_file.readlines()
    # append the robot list
    executable_plan += (log_data[8] + "\n")
    # append the floor number
    flr_no = log_data[4][12:]
    gt = log_data[9]
    executable_plan += ("floor_no = " + flr_no + "\n\n")
    executable_plan += (gt)
    trans = log_data[10][8:]
    executable_plan += ("no_trans_gt = " + trans)
    max_trans = log_data[11][12:]
    executable_plan += ("max_trans = " + max_trans + "\n")

    # append the AI to the connector and helper functions
    connector_file = Path(os.getcwd() + "/modules/ai2thor/ai2thor_connect.py").read_text()
    executable_plan += (connector_file + "\n")

    # append the allocated plan
    allocated_plan = Path(log_path + "/code_plan.py").read_text()
    brks = append_trans_ctr(allocated_plan)
    executable_plan += (allocated_plan + "\n")
    executable_plan += ("no_trans = " + str(brks) + "\n")

    # append the task thread termination
    terminate_plan = Path(os.getcwd() + "/modules/ai2thor/ai2thor_end.py").read_text()
    executable_plan += (terminate_plan + "\n")

    with open(f"{log_path}/executable_plan.py", 'w') as d:
        d.write(executable_plan)

    return f"{log_path}/executable_plan.py"


parser = argparse.ArgumentParser()
parser.add_argument("--command", type=str, required=True)
args = parser.parse_args()

expt_name = args.command
print(expt_name)
ai_exec_file = compile_aithor_exec_file(expt_name)

subprocess.run(["python", ai_exec_file])
