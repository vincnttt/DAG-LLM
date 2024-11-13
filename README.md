# DAG-LLM
LLM based Multi-robot Task Planning with Directed Acyclic Graph (DAG).

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
python3 scripts/execute_plan.py --command {plan_folder_name}
```