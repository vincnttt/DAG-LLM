# DAG-LLM：基于大语言模型的多机器人任务调度方法

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

