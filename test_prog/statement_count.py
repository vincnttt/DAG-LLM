import ast
import inspect

import sys
sys.path.append(".")


"""
Count statements inside function
"""
def count_function_steps(func):
    # Get the source code of the function
    source = inspect.getsource(func)

    # Parse the source code into an AST
    tree = ast.parse(source)

    # Locate the function definition in the AST
    func_def = next(node for node in tree.body if isinstance(node, ast.FunctionDef))

    # Count the statements in the function body
    return len(func_def.body)


def turn_off_lights():
    GoToObject('LightSwitch')
    SwitchOff('LightSwitch')
    GoToObject('LightSwitch')


# steps = count_function_steps(turn_off_lights)
# print(f"The function 'turn_off_lights' has {steps} steps.")


"""
Count statements inside function and it's function name 
"""
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


# Example usage
file_path = "./test_prog/example_def.py"  # Replace with the path to your Python file
results = analyze_python_file(file_path)

task_steps = {}
n = 1

# Print the results
for func_name, num_statements in results.items():
    # print(f"Function '{func_name}' has {num_statements} statements.")
    task_steps[n] = num_statements
    n += 1

print(task_steps)