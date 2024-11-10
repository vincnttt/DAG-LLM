# EXAMPLE 1 - Task Description: Make a french fries.
# Task Understanding: Fry a potato, then serve it on a plate.
# GENERAL TASK DECOMPOSITION
# Independent subtasks:
# Subtask 1: Slice potato (Skills required: GoToObject, PickupObject, PutObject, SliceObject).
# Subtask 2: Wash the plate. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# Subtask 3: Fry the potato. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# Subtask 4: Serve on plate. (Skills required: GoToObject, PickupObject, PutObject)
# We can parallelize Subtask 1 and Subtask 2, when Subtask 1 done, execute task 3, then execute Subtask 4 after Subtask 2 and Subtask 3 done.

# CODE
def slice_potato():
    # 0: Subtask 1: Slice potato.
    # 1: Go to the knife.
    GoToObject('Knife')
    # 2: Pick up the knife.
    PickupObject('Knife')
    # 3: Go to the potato.
    GoToObject('Potato')
    # 4: Slice the potato.
    SliceObject('Potato')
    # 5: Go to the countertop.
    GoToObject('CounterTop')
    # 6: Put the Knife back on the CounterTop.
    PutObject('Knife', 'CounterTop')

def wash_plate():
    # 0: Subtask 2: Wash the plate.
    # 1: Go to the plate.
    GoToObject('Plate')
    # 2: Pick up the plate.
    PickupObject('Plate')
    # 3: Go to the sink.
    GoToObject('Sink')
    # 4: Put the plate inside the sink.
    PutObject('Plate', 'Sink')
    # 5: Switch on the faucet to clean the plate.
    SwitchOn('Faucet')
    # 6: Wait for a while to let the plate clean.
    time.sleep(5)
    # 7: Switch off the faucet.
    SwitchOff('Faucet')
    # 8: Pick up the clean plate.
    PickupObject('Plate')
    # 9: Go to the countertop.
    GoToObject('CounterTop')
    # 10: Place the plate on the countertop.
    PutObject('Plate', 'CounterTop')

def fry_potato():
    # 0: Subtask 3: Fry the Potato.
    # 1: Go to the sliced Potato.
    GoToObject('Potato')
    # 2: Pick up the sliced Potato.
    PickupObject('Potato')
    # 3: Go to the Pan.
    GoToObject('Pan')
    # 4: Put the sliced Potato in the Pan.
    PutObject('Potato', 'Pan')
    # 5: Pick up the pan with potato in it.
    PickupObject('Pan')
    # 6: Go to the StoveBurner.
    GoToObject('StoveBurner')
    # 7: Put the Pan on the stove burner.
    PutObject('Pan', 'StoveBurner')
    # 7: Switch on the StoveKnob.
    SwitchOn('StoveKnob')
    # 7: Wait for a while to let the Potato fry.
    time.sleep(5)
    # 8: Switch off the StoveKnob.
    SwitchOff('StoveKnob')

def serve_potato_on_plate():
    # 0: Subtask 4: Serve on plate.
    # 1: Go to the Potato.
    GoToObject('Potato')
    # 2: Pick up the Potato.
    PickupObject('Potato')
    # 3: Go to the Plate.
    GoToObject('Plate')
    # 4: Put the fried Potato on the Plate.
    PutObject('Potato', 'Plate')

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better task allocation, first we need to design DAG:
# slice_potato()    wash_plate()
#       |               |
#       V               |
# fry_potato() <--------|
#       |
#       V
# serve_potato_on_plate()
# Now, implement the task allocation based from above DAG.

# Parallelize SubTask 1 and SubTask 2
task1_thread = threading.Thread(target=slice_potato)
task2_thread = threading.Thread(target=wash_plate)

# Start executing Subtask 1 and Subtask 2 in parallel
task1_thread.start()
task2_thread.start()

# Ensure Subtask 1 done before execute Subtask 3
task1_thread.join()
fry_potato()

# Wait for Subtask 2 done
task2_thread.join()

# Execute Subtask 4 when all Subtask 2 and Subtask 3 is done.
serve_potato_on_plate()

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have four main subtasks: 'Slice Potato', 'Wash the plate', 'Fry the potato' and 'Serve on plate'.
# For the 'Slice Potato' subtask, it requires 'GoToObject', 'PickupObject', 'SliceObject', and 'PutObject' skills. In this case Robot 2 has all these skills.
# For the 'Wash the plate' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 2 and robot 3 has all these skills.
# For the 'Fry the potato' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 2 and robot 3 has all these skills.
# For the 'Serve on plate' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject'. In this case Robot 2 and robot 3 has all these skills.
# Although some of the subtask can be assigned by two or more robot, but it also needs to be allocated based on availability of current robot.

# CODE Solution
def slice_potato(robots):
    # 0: Subtask 1: Slice potato.
    # 1: Go to the knife.
    GoToObject(robots, 'Knife')
    # 2: Pick up the knife.
    PickupObject(robots, 'Knife')
    # 3: Go to the potato.
    GoToObject(robots, 'Potato')
    # 4: Slice the potato.
    SliceObject(robots, 'Potato')
    # 5: Go to the countertop.
    GoToObject(robots, 'CounterTop')
    # 6: Put the Knife back on the CounterTop.
    PutObject(robots, 'Knife', 'CounterTop')

def wash_plate(robots):
    # 0: Subtask 2: Wash the plate.
    # 1: Go to the plate.
    GoToObject(robots, 'Plate')
    # 2: Pick up the plate.
    PickupObject(robots, 'Plate')
    # 3: Go to the sink.
    GoToObject(robots, 'Sink')
    # 4: Put the plate inside the sink.
    PutObject(robots, 'Plate', 'Sink')
    # 5: Switch on the faucet to clean the plate.
    SwitchOn(robots, 'Faucet')
    # 6: Wait for a while to let the plate clean.
    time.sleep(5)
    # 7: Switch off the faucet.
    SwitchOff(robots, 'Faucet')
    # 8: Pick up the clean plate.
    PickupObject(robots, 'Plate')
    # 9: Go to the countertop.
    GoToObject(robots, 'CounterTop')
    # 10: Place the plate on the countertop.
    PutObject(robots, 'Plate', 'CounterTop')

def fry_potato(robots):
    # 0: Subtask 3: Fry the Potato.
    # 1: Go to the sliced Potato.
    GoToObject(robots, 'Potato')
    # 2: Pick up the sliced Potato.
    PickupObject(robots, 'Potato')
    # 3: Go to the Pan.
    GoToObject(robots, 'Pan')
    # 4: Put the sliced Potato in the Pan.
    PutObject(robots, 'Potato', 'Pan')
    # 5: Pick up the pan with potato in it.
    PickupObject(robots, 'Pan')
    # 6: Go to the StoveBurner.
    GoToObject(robots, 'StoveBurner')
    # 7: Put the Pan on the stove burner.
    PutObject(robots, 'Pan', 'StoveBurner')
    # 7: Switch on the StoveKnob.
    SwitchOn(robots, 'StoveKnob')
    # 7: Wait for a while to let the Potato fry.
    time.sleep(5)
    # 8: Switch off the StoveKnob.
    SwitchOff(robots, 'StoveKnob')

def serve_potato_on_plate(robots):
    # 0: Subtask 4: Serve on plate.
    # 1: Go to the Potato.
    GoToObject(robots, 'Potato')
    # 2: Pick up the Potato.
    PickupObject(robots, 'Potato')
    # 3: Go to the Plate.
    GoToObject(robots, 'Plate')
    # 4: Put the fried Potato on the Plate.
    PutObject(robots, 'Potato', 'Plate')

# DIRECTED ACYCLIC GRAPH (DAG) Robot Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
# slice_potato(robots[1])    wash_plate(robots[2])
#           |                           |
#           V                           |
# fry_potato(robots[1]) <---------------|
#           |
#           V
# serve_potato_on_plate(robots[2])

# Parallelize SubTask 1 and SubTask 2
task1_thread = threading.Thread(target=slice_potato([robots[1]]))
task2_thread = threading.Thread(target=wash_plate([robots[2]]))

# Start executing Subtask 1 and Subtask 2 in parallel
task1_thread.start()
task2_thread.start()

# Ensure Subtask 1 done before execute Subtask 3
task1_thread.join()
fry_potato([robots[1]])

# Wait for Subtask 2 done
task2_thread.join()

# Execute Subtask 4 when all Subtask 2 and Subtask 3 is done.
serve_potato_on_plate([robots[2]])



# EXAMPLE 2 - Task Description: Prepare for the meeting.
# Task Understanding: Put the laptop, book, and pen to the coffee table.
# GENERAL TASK DECOMPOSITION
# Independent subtasks:
# Subtask 1: Put the laptop, book, and pen to the coffee table. (Skills required: GoToObject, PickupObject, PutObject)
# We can directly execute the Subtask 1.

# CODE
def put_things_to_coffee_table():
    # 0: Subtask 1: Put the laptop, book, and pen to the coffee table.
    # 1: Go to the laptop.
    GoToObject('Laptop')
    # 2: Pick up the laptop.
    PickupObject('Laptop')
    # 3: Go to the coffee table.
    GoToObject('CoffeeTable')
    # 4: Put the laptop to the coffee table.
    PutObject('Laptop', 'CoffeeTable')
    # 5: Go to the book.
    GoToObject('Book')
    # 6: Pick up the book.
    PickupObject('Book')
    # 7: Go to the coffee table.
    GoToObject('CoffeeTable')
    # 8: Put the book to the coffee table.
    PutObject('Book', 'CoffeeTable')
    # 9: Go to the pen.
    GoToObject('Pen')
    # 10: Pick up the pen.
    PickupObject('Pen')
    # 11: Go to the coffee table.
    GoToObject('CoffeeTable')
    # 12: Put the pen to the coffee table.
    PutObject('Pen', 'CoffeeTable')

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better task allocation, first we need to design DAG:
# put_things_to_coffee_table()
# Now, implement the task allocation based from above DAG.

# Execute subtask 1.
put_things_to_coffee_table()

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have one main subtasks: 'Put things to the coffee table'.
# For the 'Slice Potato' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject' skills. In this case Robot 2 and Robot 3 has all these skills.
# Based from explanation above, team of robots may be required, because Robot 2 and Robot 3 has meet the skills requirements and it also will make the subtask finished in shorter amount of time.
# From subtask 1, we can design sub-subtask decomposition:
# Sub-subtask 1: Put the laptop to coffee table.
# Sub-subtask 2: Put the book to coffee table.
# Sub-subtask 3: Put the pen to coffee table.
# Assign Sub-subtask 1 for Robot 2, assign Sub-subtask 2 for Robot 3, then wait for Robot 2 finishing the Sub-subtask 1 before assigning the Sub-subtask 3.

# DIRECTED ACYCLIC GRAPH (DAG) Robot Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
# Put the laptop sub-subtask(robots[1])     Put the book sub-subtask(robots[2])
#                   |                                       |
#                   V                                       |
# put the pen sub-subtask(robots[1]) <----------------------|

# CODE Solution
def put_things_to_coffee_table(robots):
    # 0: Subtask 1: Put the laptop, book, and pen to the coffee table.
    # 1: Sub-subtask 1: Put the laptop to coffee table.
    # 2: Go to the laptop.
    GoToObject(robots[1], 'Laptop')
    # 3: Pick up the laptop.
    PickupObject(robots[1], 'Laptop')
    # 4: Go to the coffee table.
    GoToObject(robots[1], 'CoffeeTable')
    # 5: Put the laptop to the coffee table.
    PutObject(robots[1], 'Laptop', 'CoffeeTable')
    # 6: Sub-subtask2: Put the book to coffee table.
    # 7: Go to the book.
    GoToObject(robots[2], 'Book')
    # 8: Pick up the book.
    PickupObject(robots[2], 'Book')
    # 9: Go to the coffee table.
    GoToObject(robots[2], 'CoffeeTable')
    # 10: Put the book to the coffee table.
    PutObject(robots[2], 'Book', 'CoffeeTable')
    # 11: Sub-subtask 3: Put the pen to coffee table.
    # 12: Go to the pen.
    GoToObject(robots[1], 'Pen')
    # 13: Pick up the pen.
    PickupObject(robots[1], 'Pen')
    # 14: Go to the coffee table.
    GoToObject(robots[1], 'CoffeeTable')
    # 15: Put the pen to the coffee table.
    PutObject(robots[1], 'Pen', 'CoffeeTable')

# Execute Subtask 1.
put_things_to_coffee_table([robots[1], robots[2]])
