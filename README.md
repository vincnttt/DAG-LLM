# DAG-LLM：基于大语言模型的多机器人任务调度方法

**摘要** 现有的多机器人任务调度方法在任务分解、 依赖管理和资源优化方面存在不足， 难以有效处理复杂任务的分配与执行。另外， 单纯依赖大语言模型（LLM） 进行任务调度容易导致任务冲突和资源浪费。 提出一种称为 DAG-LLM 任务调度方法， 该方
法首先结合环境信息与任务分解样本， 利用LLM和抽象链（CoA）进行任务理解与分解； 随后， LLM 生成任务的有向无环图（DAG），确保任务依赖关系得到正确建模； 最后， 采用回溯算法检查机器人可执行的任务， 并结合异步执行机制优化任务调度。 实验结果
表明， DAG-LLM 在 AI2-THOR 虚拟环境中的平均任务成功率是 93.3%， 比基准方法（SMART-LLM） 提高了 43.3%、 平均运行时间比基准方法缩短了 32.8%， 验证了该方法能够提升多机器人任务调度效率并增强任务执行稳定性。

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

## 数据集

本实验共有30个任务，场景包括：厨房、客厅、卧室和浴室。

可以在 `\modules\plans\` 查看并执行。

## 引用

