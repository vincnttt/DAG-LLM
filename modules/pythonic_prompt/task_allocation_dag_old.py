# EXAMPLE 1 - Task Description: Make a french fries.
# Task Understanding: Slice the potato, fry the sliced potato, then serve it on a plate.
# GENERAL TASK DECOMPOSITION
# Independent subtasks:
# Subtask 1: Slice potato (Skills required: GoToObject, PickupObject, PutObject, SliceObject).
# Subtask 2: Fry the potato. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# Subtask 3: Serve on plate. (Skills required: GoToObject, PickupObject, PutObject)
# we can execute Subtask 1 first, after Subtask 1 done, execute Subtask 2, then execute Subtask 3 after Subtask 2 done.

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

def fry_potato():
    # 0: Subtask 2: Fry the Potato.
    # 1: Go to the sliced Potato.
    GoToSlicedObject('PotatoSliced')
    # 2: Pick up the sliced Potato.
    PickupObjectSliced('PotatoSliced')
    # 3: Go to the Pan.
    GoToObject('Pan')
    # 4: Put the sliced Potato in the Pan.
    PutObjectSliced('PotatoSliced', 'Pan')
    # 5: Pick up the pan with potato in it.
    PickupObject('Pan')
    # 6: Go to the StoveBurner.
    GoToObject('StoveBurner')
    # 7: Put the Pan on the stove burner.
    PutObject('Pan', 'StoveBurner')
    # 7: Switch on the StoveKnob.
    SwitchOn('StoveKnob')
    # 7: Wait for a while to let the potato fry.
    time.sleep(5)
    # 8: Switch off the StoveKnob.
    SwitchOff('StoveKnob')

def serve_potato_on_plate():
    # 0: Subtask 3: Serve on plate.
    # 1: Go to the Potato.
    GoToSlicedObject('PotatoSliced')
    # 2: Pick up the Potato.
    PickupObjectSliced('PotatoSliced')
    # 3: Go to the Plate.
    GoToObject('Plate')
    # 4: Put the fried Potato on the Plate.
    PutObject('PotatoSliced', 'Plate')

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better task allocation, first we need to design DAG:
# slice_potato()
#       |
#       V
# fry_potato()
#       |
#       V
# serve_potato_on_plate()
# Now, implement the task allocation based from above DAG.

# Execute Subtask 1 first
slice_potato()

# After Subtask 1 done, execute Subtask 2
fry_potato()

# Execute Subtask 3 when all Subtask 2 is done.
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

def fry_potato(robots):
    # 0: Subtask 2: Fry the Potato.
    # 1: Go to the sliced potato.
    GoToSlicedObject(robots, 'Potato')
    # 2: Pick up the sliced potato.
    PickupObject(robots, 'Potato')
    # 3: Go to the Pan.
    GoToObject(robots, 'Pan')
    # 4: Put the sliced potato in the Pan.
    PutObject(robots, 'PotatoSliced', 'Pan')
    # 5: Pick up the pan with sliced potato in it.
    PickupObject(robots, 'Pan')
    # 6: Go to the StoveBurner.
    GoToObject(robots, 'StoveBurner')
    # 7: Put the Pan on the stove burner.
    PutObject(robots, 'Pan', 'StoveBurner')
    # 7: Switch on the StoveKnob.
    SwitchOn(robots, 'StoveKnob')
    # 7: Wait for a while to let the potato fry.
    time.sleep(5)
    # 8: Switch off the StoveKnob.
    SwitchOff(robots, 'StoveKnob')

def serve_potato_on_plate(robots):
    # 0: Subtask 3: Serve on plate.
    # 1: Go to the fried potato.
    GoToSlicedObject(robots, 'PotatoSliced')
    # 2: Pick up the fried potato.
    PickupObjectSliced(robots, 'PotatoSliced')
    # 3: Go to the Plate.
    GoToObject(robots, 'Plate')
    # 4: Put the fried potato on the Plate.
    PutObjectSliced(robots, 'PotatoSliced', 'Plate')

# DIRECTED ACYCLIC GRAPH (DAG) Robot Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
# slice_potato(robots[1])
#           |
#           V
# fry_potato(robots[1])
#           |
#           V
# serve_potato_on_plate(robots[2])

# Execute Subtask 1 first
slice_potato([robots[1]])

# After Subtask 1 done, execute Subtask 2
fry_potato([robots[1]])

# Execute Subtask 3 when all Subtask 2 is done.
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



# EXAMPLE 3 - Task Description: Make a toast.
# Task Understanding: Slice a bread, toast the sliced bread, then serve it on a plate.
# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
# Independent subtasks:
# Subtask 1: Slice bread. (Skills required: GoToObject, PickupObject, PutObject, SliceObject)
# Subtask 2: Toast the sliced bread. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# Subtask 3: Serve the toast on a plate. (Skills required: GoToObject, PickupObject, PutObject)
# We can execute all the Subtask in serial, start from Subtask 1, when done execute Subtask 2, then execute Subtask 3 after Subtask 3 done.

# CODE
def slice_bread():
    # 0: SubTask 1: Slice bread.
    # 1: Go to the knife.
    GoToObject('Knife')
    # 2: Pick up the knife.
    PickupObject('Knife')
    # 3: Go to the bread.
    GoToObject('Bread')
    # 4: Slice the bread.
    SliceObject('Bread')
    # 5: Go to the countertop.
    GoToObject('CounterTop')
    # 6: Put the knife back on the CounterTop.
    PutObject('Knife', 'CounterTop')

def toast_bread():
    # 0: Subtask 2: Toast the sliced bread.
    # 1: Go to the sliced bread.
    GoToSlicedObject('BreadSliced')
    # 2: Pick up the sliced bread.
    PickupSlicedObject('BreadSliced')
    # 3: Go to the toaster.
    GoToObject('Toaster')
    # 4: Put sliced bread in to the toaster.
    PutSlicedObject('BreadSliced', 'Toaster')
    # 5: Switch on the toaster.
    SwitchOn('Toaster')
    # 6: Wait for a while to let the sliced bread cooked.
    time.sleep(5)
    # 7: Switch off the toaster.
    SwitchOff('Toaster')

def serve_toast_on_plate():
    # 0: Subtask 3: Serve the toast on a plate.
    # 1: Go to the toaster.
    GoToObject('Toaster')
    # 2: Pick up the toast.
    PickupSlicedObject('BreadSliced')
    # 3: Go to the plate.
    GoToObject('Plate')
    # 4: Put the toast on a plate
    PutSlicedObject('BreadSliced', 'Plate')

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better task allocation, first we need to design DAG:
# slice_bread()
#       |
#       V
# toast_bread()
#       |
#       V
# serve_toast_on_plate()
# Now, implement the task allocation based from above DAG.

# Execute Subtask 1
slice_bread()

# Execute Subtask 2
toast_bread()

# Execute Subtask 3
serve_toast_on_plate()

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'PushObject', 'PullObject'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have four main subtasks: 'Slice bread', 'Toast the sliced bread' and 'Serve the toast on a plate'.
# For the 'Slice bread' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', and 'SliceObject'. In this case Robot 1 and Robot 2 has all these skills.
# For the 'Slice bread' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 1 and Robot 2 has all these skills.
# For the 'Slice bread' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject'. In this case Robot 1 and Robot 2 has all these skills.
# As from above solution, all subtasks can be done by Robot 1 and Robot 2, in this case we can allocate the robot based from its condition and the availability of current robot, also take care to the dependency of each subtask.

# CODE Solution
def slice_bread(robots):
    # 0: SubTask 1: Slice bread.
    # 1: Go to the knife.
    GoToObject(robots, 'Knife')
    # 2: Pick up the knife.
    PickupObject(robots, 'Knife')
    # 3: Go to the bread.
    GoToObject(robots, 'Bread')
    # 4: Slice the bread.
    SliceObject(robots, 'Bread')
    # 5: Go to the countertop.
    GoToObject(robots, 'CounterTop')
    # 6: Put the knife back on the CounterTop.
    PutObject(robots, 'Knife', 'CounterTop')

def toast_bread(robots):
    # 0: Subtask 2: Toast the sliced bread.
    # 1: Go to the sliced bread.
    GoToSlicedObject(robots, 'BreadSliced')
    # 2: Pick up the sliced bread.
    PickupSlicedObject(robots, 'BreadSliced')
    # 3: Go to the toaster.
    GoToObject(robots, 'Toaster')
    # 4: Put sliced bread in to the toaster.
    PutSlicedObject(robots, 'BreadSliced', 'Toaster')
    # 5: Switch on the toaster.
    SwitchOn(robots, 'Toaster')
    # 6: Wait for a while to let the sliced bread cooked.
    time.sleep(5)
    # 7: Switch off the toaster.
    SwitchOff(robots, 'Toaster')

def serve_toast_on_plate(robots):
    # 0: Subtask 3: Serve the toast on a plate.
    # 1: Go to the toaster.
    GoToObject(robots, 'Toaster')
    # 2: Pick up the toast.
    PickupSlicedObject(robots, 'BreadSliced')
    # 3: Go to the plate.
    GoToObject(robots, 'Plate')
    # 4: Put the toast on a plate
    PutSlicedObject(robots, 'BreadSliced', 'Plate')

# DIRECTED ACYCLIC GRAPH (DAG) Robot Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
# slice_bread(robots[0])
#           |
#           V
# toast_bread(robots[1])
#           |
#           V
# serve_toast_on_plate(robots[1])

# Now, implement the task allocation based from above DAG.

# Execute Subtask 1
slice_bread([robots[0]])

# Execute Subtask 2
toast_bread([robots[1]])

# Execute Subtask 3
serve_toast_on_plate([robots[1]])