# EXAMPLE 1 - Task Description: Make a french fries.
# Task Understanding: Slice the potato, fry the sliced potato, then serve it on a plate.
# GENERAL TASK DECOMPOSITION
# Independent subtasks:
# Subtask 1: Slice potato (Skills required: GoToObject, PickupObject, PutObject, SliceObject).
# Subtask 2: Fry the potato. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# Subtask 3: Serve on plate. (Skills required: GoToObject, PickupObject, PutObject)
# we can execute Subtask 1 first, after Subtask 1 done, execute Subtask 2, then execute Subtask 3 after Subtask 2 done.
from modules.ai2thor.ai2thor_connect import GoToObject
from test_ai2thor.ai2thor_ctrl_test import PutObject

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
# In this case, subtask 'Slice Potato' can only be done by Robot 2, then subtask 'Fry the potato' and subtask 'Serve on plate' both can be done by Robot 2 and Robot 3.

# CODE SOLUTION
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
    GoToSlicedObject(robots, 'PotatoSliced')
    # 2: Pick up the sliced potato.
    PickupSlicedObject(robots, 'PotatoSliced')
    # 3: Go to the Pan.
    GoToObject(robots, 'Pan')
    # 4: Put the sliced potato in the Pan.
    PutSlicedObject(robots, 'PotatoSliced', 'Pan')
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
    PickupSlicedObject(robots, 'PotatoSliced')
    # 3: Go to the Plate.
    GoToObject(robots, 'Plate')
    # 4: Put the fried potato on the Plate.
    PutSlicedObject(robots, 'PotatoSliced', 'Plate')

# INITIALIZE SUBTASK
subtasks = ["slice_potato", "fry_potato", "serve_potato_on_plate"]

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better task allocation, first we need to design DAG:
dependencies = [
    ("slice_potato", "fry_potato"),     # Subtask slice_potato -> Subtask fry_potato
    ("fry_potato", "serve_potato_on_plate"),    # Subtask fry_potato -> Subtask serve_potato_on_plate
]

# Based from solution, lists the robots that qualified to each subtask
qualified_robot = {
    "slice_potato": [1],    # Subtask slice_potato can be done by Robot 2
    "fry_potato": [1,2],    # Subtask fry_potato can be done by Robot 2 and Robot 3
    "serve_potato_on_plate": [1,2]      # Subtask serve_potato_on_plate can be done by Robot 2 and Robot 3
}



# EXAMPLE 2 - Task Description: Prepare for the meeting.
# Task Understanding: Put the laptop, book, and pen to the coffee table.
# GENERAL TASK DECOMPOSITION
# Independent subtasks:
# Subtask 1: Put the laptop to the coffee table. (Skills required: GoToObject, PickupObject, PutObject)
# Subtask 2: Put the book to the coffee table. (Skills required: GoToObject, PickupObject, PutObject)
# Subtask 3: Put the pen to the coffee table. (Skills required: GoToObject, PickupObject, PutObject)
# We can directly execute the Subtask 1 and Subtask 2 parallel, then when Subtask 2 is done, execute Subtask 3.

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have three main subtasks: 'Put the laptop to the coffee table', 'Put the book to the coffee table' and 'Put the pen to the coffee table'.
# For the 'Put the laptop to the coffee table' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject' skills. In this case Robot 2 and Robot 3 has all these skills.
# For the 'Put the book to the coffee table' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject' skills. In this case Robot 2 and Robot 3 has all these skills.
# For the 'Put the pen to the coffee table' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject' skills. In this case Robot 2 and Robot 3 has all these skills.
# As from above solution, all subtasks can be done by Robot 2 and Robot 3.

# CODE SOLUTION
def put_laptop_to_coffee_table(robots):
    # 0: Subtask 1: Put the laptop to the coffee table.
    # 1: Go to the laptop.
    GoToObject(robots, 'Laptop')
    # 2: Pick up the laptop.
    PickupObject(robots, 'Laptop')
    # 3: Go to the coffee table.
    GoToObject(robots, 'CoffeeTable')
    # 4: Put the laptop to the coffee table.
    PutObject(robots, 'Laptop', 'CoffeeTable')

def put_book_to_coffee_table(robots):
    # 0: Subtask 2: Put the book to the coffee table.
    # 1: Go to the book.
    GoToObject(robots, 'Book')
    # 2: Pick up the book.
    PickupObject(robots, 'Book')
    # 3: Go to the coffee table.
    GoToObject(robots, 'CoffeeTable')
    # 4: Put the book to the coffee table.
    PutObject(robots, 'Book', 'CoffeeTable')

def put_pen_to_coffee_table(robots):
    # 0: Subtask 3: Put the pen to the coffee table.
    # 1: Go to the pen.
    GoToObject(robots, 'Pen')
    # 2: Pick up the pen.
    PickupObject(robots, 'Pen')
    # 3: Go to the coffee table.
    GoToObject(robots, 'CoffeeTable')
    # 4: Put the pen to the coffee table.
    PutObject(robots, 'Pen', 'CoffeeTable')

# INITIALIZE SUBTASK
subtasks = ["put_laptop_to_coffee_table", "put_book_to_coffee_table", "put_pen_to_coffee_table"]

# DIRECTED ACYCLIC GRAPH (DAG) Robot Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
dependencies = [
    ("put_laptop_to_coffee_table", "put_book_to_coffee_table"),  # Subtask put_laptop_to_coffee_table -> Subtask put_book_to_coffee_table
    ("put_book_to_coffee_table", "put_pen_to_coffee_table"),    # Subtask put_book_to_coffee_table -> Subtask put_pen_to_coffee_table
]

# Based from solution, lists the robots that qualified to each subtask
qualified_robot = {
    "put_laptop_to_coffee_table": [1,2],    # Subtask put_laptop_to_coffee_table can be done by Robot 2 and Robot 3
    "put_book_to_coffee_table": [1,2],  # Subtask put_book_to_coffee_table can be done by Robot 2 and Robot 3
    "put_pen_to_coffee_table": [1,2],   # Subtask put_pen_to_coffee_table can be done by Robot 2 and Robot 3
}



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

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'PushObject', 'PullObject'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'DropHandObject', 'ThrowObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have three main subtasks: 'Slice bread', 'Toast the sliced bread' and 'Serve the toast on a plate'.
# For the 'Slice bread' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', and 'SliceObject'. In this case Robot 1 and Robot 2 has all these skills.
# For the 'Toast the sliced bread' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 1 and Robot 2 has all these skills.
# For the 'Serve the toast on a plate' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject'. In this case Robot 1 and Robot 2 has all these skills.
# As from above solution, all subtasks can be done by Robot 1 and Robot 2.

# CODE SOLUTION
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

# INITIALIZE SUBTASK
subtasks = ["slice_bread", "toast_bread", "serve_toast_on_plate"]

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
dependencies = [
    ("slice_bread", "toast_bread"),     # Subtask slice_bread -> Subtask toast_bread
    ("toast_bread", "serve_toast_on_plate"),    # Subtask toast_bread -> Subtask serve_toast_on_plate
]

# Based from solution, lists the robots that qualified to each subtask
qualified_robot = {
    "slice_bread": [0,1],    # Subtask slice_bread can be done by Robot 1 and Robot 2
    "toast_bread": [0,1],    # Subtask toast_bread can be done by Robot 1 and Robot 2
    "serve_toast_on_plate": [0,1]      # Subtask serve_toast_on_plate can be done by Robot 1 and Robot 2
}



# EXAMPLE 4 - Task Description: Store food in the fridge and make a coffee.
# Task Understanding: Store perishable items to the fridge, and make a cup of coffee.
# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
# Independent subtasks:
# Subtask 1: Store perishable items to fridge. (Skills required: GoToObject, PickupObject, PutObject, OpenObject, CloseObject)
# Subtask 2: Make a cup of coffee. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# We can execute all Subtask in parallel.

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'PushObject', 'PullObject'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'ThrowObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have two main subtasks: 'Store perishable items to fridge' and 'Make a cup of coffee'.
# For the 'Store perishable items to fridge' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', 'OpenObject', and 'CloseObject'. In this case Robot 2 and Robot 3 has all these skills.
# For the 'Make a cup of coffee' subtask, it requires 'GoToObject', 'PickupObject', 'PutObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 3 has all these skills.
# As from above solution, subtask 'Store perishable items to fridge' can be done by Robot 2 and Robot 3, subtask 'Make a cup of coffee' can only be done by Robot 3

# CODE SOLUTION
def store_perishable_items_to_fridge(robots):
    # 0: Subtask 1: Store perishable items to the fridge
    # 1: Go to the lettuce.
    GoToObject(robots, 'Lettuce')
    # 2: Pick up the lettuce.
    PickupObject(robots, 'Lettuce')
    # 3: Go to the fridge.
    GoToObject(robots, 'Fridge')
    # 4: Open the fridge
    OpenObject(robots, 'Fridge')
    # 5: Put the lettuce to the fridge.
    PutObject(robots, 'Lettuce', 'Fridge')
    # 6: Go to the tomato.
    GoToObject(robots, 'Tomato')
    # 7: Pick up the tomato.
    PickupObject(robots, 'Tomato')
    # 8: Go to the fridge.
    GoToObject(robots, 'Fridge')
    # 9: Put the tomato to the fridge.
    PutObject(robots, 'Tomato', 'Fridge')
    # 10: Go to the apple.
    GoToObject(robots, 'Apple')
    # 11: Pick up the apple.
    PickupObject(robots, 'Apple')
    # 12: Go to the fridge.
    GoToObject(robots, 'Fridge')
    # 13: Put the apple to the fridge.
    PutObject(robots, 'Apple', 'Fridge')
    # 14: Close the fridge when all items stored.
    CloseObject(robots, 'Fridge')

def make_a_coffee(robots):
    # 0: Subtask 1: Make a cup of coffee.
    # 1: Go to the mug.
    GoToObject(robots, 'Mug')
    # 2: Pick up the mug.
    PickupObject(robots, 'Mug')
    # 3: Go to the coffee machine.
    GoToObject(robots, 'CoffeeMachine')
    # 4: Put Mug in to the coffee machine
    PutObject(robots, 'Mug', 'CoffeeMachine')
    # 5: Turn on the coffee machine.
    SwitchOn(robots, 'CoffeeMachine')
    # 6: Wait for a while to let the mug filled with coffee.
    time.sleep(5)
    # 7: Turn off the coffee machine.
    SwitchOff(robots, 'CoffeeMachine')
    # 8: Pick up the mug of coffee.
    PickupObject(robots, 'Mug')
    # 9: Go to the countertop.
    GoToObject(robots, 'CounterTop')
    # 10: Put mug of coffee in to the countertop.
    PutObject(robots, 'Mug', 'CounterTop')

# INITIALIZE SUBTASK
subtasks = ["store_perishable_items_to_fridge", "make_a_coffee"]

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
dependencies = []   # No dependencies, tasks can be executed in parallel

# Based from solution, lists the robots that qualified to each subtask
qualified_robot = {
    "make_a_coffee": [1,2],    # Subtask make_a_coffee can be done by Robot 2 and Robot 3
    "store_perishable_items_to_fridge": [2],    # Subtask store_perishable_items_to_fridge can only be done by Robot 3
}



# EXAMPLE 5 - Task Description: Trash the newspaper, then turn on the laptop and television.
# Task Understanding: Throw the newspaper to the garbage can, turn on laptop, and turn on television.
# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
# Independent subtasks:
# Subtask 1: Throw the newspaper to the garbage can. (Skills required: GoToObject, PickupObject, PutObject)
# Subtask 2: Turn on laptop. (Skills required: GoToObject, SwitchOn, SwitchOff)
# Subtask 3: Turn on television. (Skills required: GoToObject, SwitchOn, SwitchOff)
# We can execute all Subtask in parallel.

# TASK ALLOCATION
robots = [
    {'name': 'robot1', 'skills': ['GoToObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff'], 'mass': 100},
    {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'SliceObject', 'PickupObject', 'PutObject', 'SwitchOn', 'SwitchOff', 'ThrowObject'],'mass': 100},
    {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'PickupObject', 'PutObject'], 'mass': 100}
]
# SOLUTION
# All the robots DO NOT share the same set and number (no_skills) of skills. In this case where all robots have different sets of skills - Focus on Task Allocation based on Robot Skills alone.
# Analyze the skills required for each subtask and the skills each robot possesses. In this scenario, we have three main subtasks: 'Throw the newspaper to the garbage can', 'Turn on laptop' and 'Turn on television'.
# For the 'Throw the newspaper to the garbage can' subtask, it requires 'GoToObject', 'PickupObject', and 'PutObject'. In this case Robot 3 has all these skills.
# For the 'Turn on laptop' subtask, it requires 'GoToObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 1 and Robot 2 has all these skills.
# For the 'Turn on television' subtask, it requires 'GoToObject', 'SwitchOn', and 'SwitchOff'. In this case Robot 1 and Robot 2 has all these skills.
# As from above solution, subtask 'Store perishable items to fridge' can be done by Robot 2 and Robot 3, subtask 'Make a cup of coffee' can only be done by Robot 3

# CODE SOLUTION
def throw_the_newspaper_to_the_garbage_can(robots):
    # 0: Subtask 1: Throw the newspaper to the garbage can.
    # 1: Go to the newspaper.
    GoToObject(robots, 'NewsPaper')
    # 2: Pick up the newspaper.
    PickupObject(robots, 'NewsPaper')
    # 3: Go to the garbage can.
    GoToObject(robots, 'GarbageCan')
    # 4: Throw newspaper to the garbage can.
    PutObject(robots, 'NewsPaper', 'GarbageCan')

def make_a_coffee(robots):
    # 0: Subtask 1: Make a cup of coffee.
    # 1: Go to the mug.
    GoToObject(robots, 'Mug')
    # 2: Pick up the mug.
    PickupObject(robots, 'Mug')
    # 3: Go to the coffee machine.
    GoToObject(robots, 'CoffeeMachine')
    # 4: Put Mug in to the coffee machine
    PutObject(robots, 'Mug', 'CoffeeMachine')
    # 5: Turn on the coffee machine.
    SwitchOn(robots, 'CoffeeMachine')
    # 6: Wait for a while to let the mug filled with coffee.
    time.sleep(5)
    # 7: Turn off the coffee machine.
    SwitchOff(robots, 'CoffeeMachine')
    # 8: Pick up the mug of coffee.
    PickupObject(robots, 'Mug')
    # 9: Go to the countertop.
    GoToObject(robots, 'CounterTop')
    # 10: Put mug of coffee in to the countertop.
    PutObject(robots, 'Mug', 'CounterTop')

# INITIALIZE SUBTASK
subtasks = ["store_perishable_items_to_fridge", "make_a_coffee"]

# DIRECTED ACYCLIC GRAPH (DAG) Task Allocation
# For better robot allocation based from given subtask and robot that fulfill the skill requirements, DAG are required:
dependencies = []   # No dependencies, tasks can be executed in parallel

# Based from solution, lists the robots that qualified to each subtask
qualified_robot = {
    "make_a_coffee": [1,2],    # Subtask make_a_coffee can be done by Robot 2 and Robot 3
    "store_perishable_items_to_fridge": [2],    # Subtask store_perishable_items_to_fridge can only be done by Robot 3
}