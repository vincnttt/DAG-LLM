# DAG-LLM：基于大语言模型的多机器人任务调度方法

**摘要** 多机器人任务调度在任务分解、依赖管理与资源优化方面仍存在不足，难以有效应对复杂任务的分配与执行问题。同时，单纯依赖大语言模型（LLM）进行任务调度，容易引发任务冲突与资源浪费。针对上述问题，提出一种称为DAG-LLM的多机器人任务调度方法。该方法首先结合环境信息与任务分解样本，利用LLM和抽象链（CoA）完成任务理解，随后对任务进行分解为一组独立的子任务；其次，通过LLM对每个子任务生成任务的有向无环图（DAG），准确建模任务间的依赖关系；最后，采用回溯算法筛选机器人可执行的任务，并结合异步执行机制实现高效调度。与经典基于启发式或性能模型的DAG调度算法相比，DAG-LLM能直接从自然语言生成任务依赖并优化分配。实验在AI2-THOR虚拟环境中进行，并设计三种不同任务类型与四个场景中验证了所提方法的有效性。结果表明，DAG-LLM的平均任务成功率达到 93.3%，较基准方法SMART-LLM提高了43.3%；平均运行时间较基准方法缩短了32.8%。定量评估结果充分证明了DAG-LLM方法在提升多机器人任务调度效率与执行稳定性方面具有显著优势。消融实验进一步验证DAG-LLM方法对提升成功率，以及异步执行在减少任务执行等待方面的有效性。

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

### 数据集细节

#### 任务指令
1. Make a toast for breakfast
2. Give me a plate of salad
3. Give me coffee, then make room dark
4. Give me a plate of french fries
5. Store the apple into cold place
6. Give me a plate of fried egg
7. Throw vegetables to garbage can
8. Make a coffee for breakfast
9. Wash vegetables then store in the fridge
10. Make a toast and coffee for breakfast, make a plate of salad, throw egg to trash, then turn off light
11. Prepare for the meeting
12. I want to watch news
13. I want to watch TV, and make the room dark
14. Put the keychain and credit card into drawer
15. Turn on laptop, and put the watch in to the drawer, then turn off the floor lamp
16. Put the newspaper and remote control to the coffee table, then turn on the television
17. Trash the vase and newspaper
18. Make the room dark
19. Put the statue in to the box, then place the box in the coffee table
20. Place the keychain inside drawer, then trash the newspaper
21. Turn on the laptop and television, then make the room dark
22. Put credit card and keychain to the box, throw newspaper to garbage, turn on television and laptop, turn off floorlamp, then put tissue box to dining table
23. Turn off desk lamp
24. Put CD and Cellphone into drawer, and turn on laptop
25. Put tennis racket and vase into box
26. Close the blinds
27. Turn on Shower head, then close Shower curtain
28. Put Toilet paper into trash, then make room dark
29. Put Soap bottle into bathtub
30. Throw the cloth into trash and turn off the light

#### 任务分类
- A 类，A 类任务设置为单机器人单任务，是指仅有一个任务并且由一台机器人完成的，并且步骤比较少。A 类任务包含抽象化任务。
  - A 类任务：1，2，4，5，6，8，12，18，23，26，29
- B 类，B 类任务与 A 类任务的不同是，每台机器人仅有一个任务，但任务中涉及到多个物体以及多个步骤来完成任务。B 类任务包含少量抽象化任务，偏向于调度和分配问题。
  - B 类任务：3，7，9，11，13，14，17，20，21，25，27，28
- C 类，C 类任务涉及到多机器人多子任务，每台机器人有多个任务，并且任务中涉及到多个物体和多个步骤来完成任务。C 类任务无抽象化任务，主要重点专注于调度和分配问题。
  - C 类任务：10，15，16，19，22，24，30

## 引用

