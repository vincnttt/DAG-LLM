# EXAMPLE 1 - Task Description: Make the room dark.
# Task Understanding: Turn off the lights and turn off the floor lamp.

# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
# Independent subtasks:
# Subtask 1: Turn off the lights. (Skills required: GoToObject, SwitchOn, SwitchOff)
# Subtask 2: Turn off the floor lamp. (Skills required: GoToObject, SwitchOn, SwitchOff)
# We can parallelize Subtask 1 and Subtask 2, because they don't depend on each other.

# CODE
def turn_off_lights():
    # 0: Subtask 1: Turn off the lights.
    # 1: Go to the light switch.
    GoToObject('LightSwitch')
    # 2: Turn off the lights.
    SwitchOff('LightSwitch')

def turn_off_floor_lamp():
    # 0: Subtask 2: Turn off the floor lamp.
    # 1: Go to the floor lamp.
    GoToObject('FloorLamp')
    # 2: Turn off the floor lamp.
    SwitchOff('FloorLamp')

# Parallelize Subtask 1 and Subtask 2
task1_thread = threading.Thread(target=turn_off_lights)
task2_thread = threading.Thread(target=turn_off_floor_lamp)

# Start executing Subtask 1 and Subtask 2 in parallel.
task1_thread.start()
task2_thread.start()

# Wait for both Subtask 1 and Subtask 2 to finish.
task1_thread.join()
task2_thread.join()

# Task make the room dark is done.



# EXAMPLE 2 - Task Description: Make a sandwich for breakfast.
# Task Understanding: Cook an egg, slice lettuce, slice tomato and slice bread, then serve it on a plate.

# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
# Independent subtasks:
# Subtask 1: Cook an egg. (Skills required: GoToObject, PickupObject, PutObject, OpenObject, CloseObject, SwitchOn, SwitchOff)
# Subtask 2: Slice lettuce, tomato and bread. (Skills required: GoToObject, PickupObject, PutObject, SliceObject)
# Subtask 3: Wash a plate. (Skills required: GoToObject, PickupObject, PutObject, SwitchOn, SwitchOff)
# Subtask 4: Assemble the sandwich. (Skills required: GoToObject, PickupObject, PutObject)
# We can parallelize the Subtask 1 and Subtask 2, and when Subtask 1 done execute Subtask 3, then execute Subtask 4.

# CODE
def cook_egg():
    # 0: Subtask 1: Cook an egg.
    # 1: Go to the egg.
    GoToObject('Egg')
    # 2: Pick up the egg.
    PickupObject('Egg')
    # 3: Walk towards the microwave.
    GoToObject('Microwave')
    # 4: Open the microwave door.
    OpenObject('Microwave')
    # 5: Put the egg inside the microwave.
    PutObject('Egg', 'Microwave')
    # 6: Close the microwave
    CloseObject('Microwave')
    # 7: Switch on microwave.
    SwitchOn('Microwave')
    # 8: Wait for a while to let the egg cook.
    time.sleep(5)
    # 9: Switch off microwave.
    SwitchOff('Microwave')
    # 10: Open the microwave door.
    OpenObject('Microwave')
    # 11: Take the mgg out.
    PickupObject('Egg')
    # 12: Close the microwave.
    CloseObject('Microwave')

def slice_ingredients():
    # 0: SubTask 2: Slice lettuce, tomato and bread.
    # 1: Go to the knife.
    GoToObject('Knife')
    # 2: Pick up the knife.
    PickupObject('Knife')
    # 3: Go to the lettuce.
    GoToObject('Lettuce')
    # 4: Slice the lettuce.
    SliceObject('Lettuce')
    # 5: Go to the tomato.
    GoToObject('Tomato')
    # 6: Slice the tomato.
    SliceObject('Tomato')
    # 7: Go to the bread.
    GoToObject('Bread')
    # 8: Slice the bread.
    SliceObject('Bread')
    # 9: Go to the countertop.
    GoToObject('CounterTop')
    # 10: Put the knife back on the countertop.
    PutObject('Knife', 'CounterTop')

def wash_plate():
    # 0: SubTask 3: Wash the plate.
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

def assemble_sandwich():
    # 0: SubTask 4: Assemble the Sandwich
    # 1: Go to the sliced bread.
    GoToSlicedObject('BreadSliced')
    # 2: Pick up the sliced bread.
    PickupSlicedObject('BreadSliced')
    # 3: Go to the plate.
    GoToObject('Plate')
    # 4: Place a slice of bread on the plate.
    PutSlicedObject('BreadSliced', 'Plate')
    # 5: Go to the sliced lettuce.
    GoToSlicedObject('LettuceSliced')
    # 6: Pick up the sliced lettuce.
    PickupSlicedObject('LettuceSliced')
    # 7: Go to the plate.
    GoToObject('Plate')
    # 8: Place a slice of lettuce on the plate.
    PutSlicedObject('LettuceSliced', 'Plate')
    # 9: Go to the sliced tomato.
    GoToSlicedObject('TomatoSliced')
    # 10: Pick up the sliced tomato.
    PickupSlicedObject('TomatoSliced')
    # 11: Go to the plate.
    GoToObject('Plate')
    # 12: Place a slice of tomato on the plate.
    PutSlicedObject('TomatoSliced', 'Plate')
    # 13: Go to the egg.
    GoToObject('Egg')
    # 14: Pick up the egg.
    PickupObject('Egg')
    # 15: Go to the plate.
    GoToObject('Plate')
    # 16: Place a slice of egg on the plate.
    PutObject('Egg', 'Plate')


# Parallelize SubTask 1 and SubTask 2
task1_thread = threading.Thread(target=cook_egg)
task2_thread = threading.Thread(target=slice_ingredients)

# Start executing Subtask 1 and Subtask 2 in parallel.
task1_thread.start()
task2_thread.start()

# Ensure Subtask 1 done before execute Subtask 3.
task1_thread.join()
wash_plate()

# Wait for Subtask 2 done.
task2_thread.join()

# Execute Subtask 4 when all Subtask is done.
assemble_sandwich()

# Task make a sandwich for breakfast is done.



# EXAMPLE 3 - Task Description: Prepare for the meeting.
# Task Understanding: Put the laptop, book, and pen to the coffee table.
# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
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

# Execute subtask 1.
put_things_to_coffee_table()



# EXAMPLE 4 - Task Description: Make a toast.
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

# Execute Subtask 1
slice_bread()

# Execute Subtask 2
toast_bread()

# Execute Subtask 3
serve_toast_on_plate()