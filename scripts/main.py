import os
import re
import json
import argparse
from datetime import datetime

from openai import OpenAI
from zhipuai import ZhipuAI
from anthropic import Anthropic

import sys
sys.path.append(".")

import ai2thor.controller
import configs.actions as actions
import configs.robots as robots


def llm(prompt, llm_type, max_tokens=128, temperature=0):
    base_url = "https://api.uniapi.me/v1"

    # Used LLM:
    # OpenAI: gpt-4o
    # Zhipu: glm-4-0520
    # Anthropic: claude-3-5-sonnet-20241022

    with open('key.txt', 'r') as f:
        api_key = f.read()

    client_openai = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    client_zhipuai = ZhipuAI(
        base_url=base_url,
        api_key=api_key
    )

    if llm_type == "gpt-4o":
        response = client_openai.chat.completions.create(model=llm_type,
                                                         messages=prompt,
                                                         max_tokens=max_tokens,
                                                         temperature=temperature)

        response_msg = response.choices[0].message.content
        return response, response_msg

    elif llm_type == "glm-4":
        response = client_zhipuai.chat.completions.create(model=llm_type,
                                                          messages=prompt,
                                                          max_tokens=max_tokens,
                                                          temperature=temperature)

        response_msg = response.choices[0].message.content
        return response, response_msg

    elif llm_type == "claude-3-5-sonnet-20240620":
        response = client_openai.chat.completions.create(model=llm_type,
                                                         messages=prompt,
                                                         max_tokens=max_tokens,
                                                         temperature=temperature)

        response_msg = response.choices[0].message.content
        return response, response_msg

    else:
        print("Invalid LLM")


# Function returns object list with name and properties.
def convert_to_dict_objprop(objs, obj_mass):
    objs_dict = []
    for i, obj in enumerate(objs):
        obj_dict = {'name': obj, 'mass': obj_mass[i]}
        objs_dict.append(obj_dict)

    return objs_dict


# Function of connector to ai2thor to get object list
def get_ai2_thor_objects(floor_plan_id):
    controller = ai2thor.controller.Controller(scene="FloorPlan" + str(floor_plan_id))
    obj = list([obj["objectType"] for obj in controller.last_event.metadata["objects"]])
    obj_mass = list([obj["mass"] for obj in controller.last_event.metadata["objects"]])
    controller.stop()
    obj = convert_to_dict_objprop(obj, obj_mass)

    return obj


# Function to comment all text outside the codeblocks
def comment_outside_codeblocks(input_text):
    # Regular expression to match Python code blocks
    code_block_pattern = r'```python(.*?)```'

    # Split the input text into sections based on code blocks
    sections = re.split(code_block_pattern, input_text, flags=re.DOTALL)

    # Initialize a list to store the final output
    final_output = []

    for i, section in enumerate(sections):
        if i % 2 == 0:
            # This is a non-code section; comment each line
            for line in section.splitlines():
                if line.strip():  # Comment only non-empty lines
                    final_output.append(f"# {line.strip()}\n")
        else:
            # This is a code block; keep it as is
            final_output.append(f"```python{section}```")

    # Join the final output
    return ''.join(final_output)


# Function to remove codeblocks
def remove_codeblocks(input_text):
    # Regular expression to match the ```python ... ``` pattern
    pattern = r"```python\s*(.*?)\s*```"

    # Use re.sub to replace the matched pattern with just the code inside
    cleaned_text = re.sub(pattern, r'\1', input_text, flags=re.DOTALL)

    return cleaned_text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--floor-plan", type=int, required=True)

    parser.add_argument("--llm", type=str, required=True,
                        choices=["gpt-4o", "claude-3-5-sonnet-20240620", "glm-4"])

    parser.add_argument("--prompt-decompose-set", type=str, default="task_decompose",
                        choices=["task_decompose"])

    parser.add_argument("--prompt-allocation-set", type=str, default="task_allocation_dag",
                        choices=["task_allocation_dag"])

    parser.add_argument("--env-plans", type=str, default="plans",
                        choices=["plans"])

    parser.add_argument("--log-results", type=bool, default=True)

    args = parser.parse_args()

    if not os.path.isdir(f"./outputs/"):
        os.makedirs(f"./outputs/")

    # Read tasks
    test_tasks = []
    robots_test_tasks = []
    gt_test_tasks = []
    trans_cnt_tasks = []
    max_trans_cnt_tasks = []

    with open(f"./modules/{args.env_plans}/FloorPlan{args.floor_plan}.json", "r") as f:
        for line in f.readlines():
            test_tasks.append(list(json.loads(line).values())[0])
            robots_test_tasks.append(list(json.loads(line).values())[1])
            gt_test_tasks.append(list(json.loads(line).values())[2])
            trans_cnt_tasks.append(list(json.loads(line).values())[3])
            max_trans_cnt_tasks.append(list(json.loads(line).values())[4])

    print(f"\n----Test set tasks----\n{test_tasks}\nTotal: {len(test_tasks)} tasks\n")

    # Prepare list of robots for the tasks
    available_robots = []
    for robots_list in robots_test_tasks:
        task_robots = []
        for i, r_id in enumerate(robots_list):
            robot = robots.robots[r_id - 1]
            # rename the robot
            robot['name'] = 'robot' + str(i + 1)
            task_robots.append(robot)
        available_robots.append(task_robots)

    """
    Train Task Decomposition
    """

    # Prepare train decomposition demonstration for ai2thor samples
    prompt = f"\nfrom skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"
    objects_ai = f"\n\nobjects = {get_ai2_thor_objects(args.floor_plan)}"
    prompt += objects_ai

    print("[STAGE 1]: ", prompt)

    # Read input train prompts
    decompose_prompt_file = open(os.getcwd() + "/modules/pythonic_prompt/" + args.prompt_decompose_set + ".py", "r")
    decompose_prompt = decompose_prompt_file.read()
    decompose_prompt_file.close()

    prompt += "\n\n" + decompose_prompt

    print("[STAGE 2]: ", prompt)

    print("Generating Decomposed Plans...")

    decomposed_plan = []
    for task in test_tasks:
        curr_prompt = f"{prompt}\n\n# Task Description: {task}"

        # Pass to LLM
        messages = [{"role": "user", "content": curr_prompt}]
        _, text = llm(messages, args.llm, max_tokens=1500)

        # decomposed_plan.append(text)
        text = comment_outside_codeblocks(text)
        decomposed_plan.append(remove_codeblocks(text))

    print("[STAGE 3]: ", decomposed_plan)

    """
    Train Task Allocation + DAG
    """

    prompt = f"\nfrom skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"
    prompt += objects_ai

    code_plan = []

    prompt_file1 = os.getcwd() + "/modules/pythonic_prompt/" + args.prompt_allocation_set + "_code.py"
    code_prompt_file = open(prompt_file1, "r")
    code_prompt = code_prompt_file.read()
    code_prompt_file.close()

    prompt += "\n\n" + code_prompt + "\n\n"

    # for i, (plan, solution) in enumerate(zip(decomposed_plan, allocated_plan)):
    for i, plan in enumerate(decomposed_plan):
        robot_n = len(available_robots[i])
        curr_prompt = prompt + plan
        curr_prompt += f"\n# TASK ALLOCATION"
        curr_prompt += f"\n# Scenario: There are {robot_n} robots available, The task should be performed using the minimum number of robots necessary. Robots should be assigned to subtasks that match its skills. Using your reasoning come up with a solution to satisfy all constraint, you may need Directed Acyclic Graph (DAG) method to make task allocation better."
        curr_prompt += f"\n\nrobots = {available_robots[i]}"
        curr_prompt += f"\n{objects_ai}"
        # curr_prompt += solution
        curr_prompt += f"\n\n# IMPORTANT: The AI should ensure that the robots assigned to the tasks have all the necessary skills to perform the tasks. IMPORTANT: Determine whether the subtasks must be performed sequentially or in parallel, or a combination of both and allocate robots based on availability. IMPORTANT: Directed Acyclic Graph (DAG) method are neccesary for task allocation. "
        curr_prompt += f"\n# CODE Solution  \n"

        if args.llm == "gpt-4o":
            messages = [
                {"role": "system",
                 "content": "You are a Robot Task Allocation Expert. Determine whether the subtasks must be performed sequentially or in parallel, or a combination of both based on your reasoning. In the case of Task Allocation based on Robot Skills alone - First check if robot teams are required. Then Ensure that robot skills or robot team skills match the required skills for the subtask when allocating. Make sure that condition is met. Make sure that condition is met. In the Task Allocation based on Skill, if there are multiple options for allocation, pick the best available option by reasoning to the best of your ability. IMPORTANT: Directed Acyclic Graph (DAG) method are neccesary to make task allocation better."},
                {"role": "user", "content": curr_prompt}
            ]
            _, text = llm(messages, args.llm, max_tokens=1400)

        else:
            messages = [
                {"role": "assistant",
                 "content": "You are a Robot Task Allocation Expert. Determine whether the subtasks must be performed sequentially or in parallel, or a combination of both based on your reasoning. In the case of Task Allocation based on Robot Skills alone - First check if robot teams are required. Then Ensure that robot skills or robot team skills match the required skills for the subtask when allocating. Make sure that condition is met. Make sure that condition is met. In the Task Allocation based on Skill, if there are multiple options for allocation, pick the best available option by reasoning to the best of your ability. IMPORTANT: Directed Acyclic Graph (DAG) method are neccesary to make task allocation better."},
                {"role": "user", "content": curr_prompt}
            ]
            _, text = llm(messages, args.llm, max_tokens=1400)

        if args.llm == "gpt-4o" or args.llm == "claude-3-5-sonnet-20240620":
            text = comment_outside_codeblocks(text)
            code_plan.append(remove_codeblocks(text))
        else:
            code_plan.append(text)

        print("[STAGE 4]: ", code_plan)

    # Save generated plans
    exec_folders = []
    if args.log_results:
        line = {}
        now = datetime.now()  # current date and time
        date_time = now.strftime("%Y-%m-%d-%H-%M-%S")

        for idx, task in enumerate(test_tasks):
            task_name = "{fxn}".format(fxn='_'.join(task.split(' ')))
            task_name = task_name.replace('\n', '')
            folder_name = f"{task_name}_plans_{date_time}"
            exec_folders.append(folder_name)

            os.mkdir("./outputs/" + folder_name)

            with open(f"./outputs/{folder_name}/log.txt", 'w') as f:
                f.write(task)
                f.write(f"\n\nLLM Type  : {args.llm}")
                f.write(f"\n\nFloor Plan: {args.floor_plan}")
                f.write(f"\n{objects_ai}")
                f.write(f"\nrobots = {available_robots[idx]}")
                f.write(f"\nground_truth = {gt_test_tasks[idx]}")
                f.write(f"\ntrans = {trans_cnt_tasks[idx]}")
                f.write(f"\nmax_trans = {max_trans_cnt_tasks[idx]}")

            with open(f"./outputs/{folder_name}/decomposed_plan.py", 'w') as d:
                d.write(decomposed_plan[idx])

            # with open(f"./outputs/{folder_name}/allocated_plan.py", 'w') as a:
            #     a.write(allocated_plan[idx])

            with open(f"./outputs/{folder_name}/code_plan.py", 'w') as x:
                x.write(code_plan[idx])
