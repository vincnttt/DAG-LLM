# DAG-LLM：基于大语言模型的多机器人任务调度方法

**摘要** 由于大语言模型（LLM）在多机器人复杂任务调度场景中容易出现错误，针对该问题，本文提出了一种称为DAG-LLM任务调度优化方法，该方法包含三个关键步骤：第一，结合环境中的物体和任务分解样本生成提示语，并利用LLM进行任务分解；第二，大语言模型分析子任务的优先级和依赖关系，生成有向无环图（DAG），确保任务按正确顺序执行；第三，通过回溯算法递归检查机器人是否能够处理所有下游依赖关系，并计算DAG图中的子任务与机器人分配列表，实现符合所有任务依赖的最优分配。实验在AI2-THOR虚拟环境中进行，结果表明，DAG-LLM平均任务成功率达到 93.3%，平均运行时间与基准方法相比减少约 32.8%，验证了该方法在多机器人任务调度中的有效性。

## 运行方法

* 需要 Python `3.10` 或以上

* 创建 `key.txt` 到根目录，并输入OpenAI key

* 下载依赖库：
```commandline
pip install -r requirments.txt
```

* 运行脚本：
```commandline
python3 scripts/main.py --floor-plan {floor_plan_num} --llm {llm}
```
`--floor-plan` 选择Floorplan编号在 `/modules/plans/FloorPlan{num}.json`

`--llm` 选择LLM（GPT-4o）

* 执行生成结果：
```commandline
python3 scripts/execute_plan.py --folder {plan_folder_name}
```

`--folder` 输入生成结果的文件夹命名

## Dataset

本实验共有30个任务，场景包括：厨房、客厅、卧室和浴室。

可以在 `\modules\plans\` 查看并执行。

## Citation

