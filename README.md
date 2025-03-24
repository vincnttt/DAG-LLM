# DAG-LLM: Multi-Robot Task Scheduling Optimization Method Based on Large Language Models

**Abstract** Because the Large Language Model (LLM) is prone to errors in the complex task scheduling scenario of multiple robots, this paper proposes a task scheduling optimization method called DAG-LLM, which contains three key steps: First, generate a prompt by combining the objects and task decomposition samples in the environment, and use LLM to decompose the task; Second, the large language model analyzes the priorities and dependencies of subtasks and generates a Directed Acyclic Graph (DAG) to ensure that tasks are executed in the correct order; Third, the backtracking algorithm recursively checks whether the robot can handle all downstream dependencies, and calculates the subtask and robot assignment list in the DAG diagram to achieve the optimal assignment that meets all task dependencies. The experiment is carried out in AI2-THOR virtual environment. The results show that the average task success rate of DAG-LLM is 93.3%, and the average running time is reduced by about 32.8% compared with the benchmark method. The effectiveness of this method in multi robot task scheduling is verified.

## Usage

Require Python `3.10` or above.

* Install dependencies:
```commandline
pip install -r requirments.txt
```

* Run script:

```commandline
python3 scripts/main.py --floor-plan {floor_plan_num} --llm {llm}
```
`--floor-plan` Number of plan environment inside `/modules/plans/FloorPlan{num}.json`.

`--llm` LLM types.

* Execute generated plan:
```commandline
python3 scripts/execute_plan.py --folder {plan_folder_name}
```

## Dataset


## Results


## Citation

