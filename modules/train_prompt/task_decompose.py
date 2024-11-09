# EXAMPLE 1 - Task Description: Make the room dark.
# Task Understanding: Turn off the lights and turn off the floor lamp.

# GENERAL TASK DECOMPOSITION
# Task Description are the given task, which is described in abstract way.
# Task Understanding are the generalized task, learn based from this pattern.
# Decompose and parallelize subtasks wherever possible.
# Independent subtasks:
# Subtask 1: Turn off the lights. (GoToObject, SwitchOn, SwitchOff)
# Subtask 2: Turn off the floor lamp. (GoToObject, SwitchOn, SwitchOff)
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
# Subtask 1: Cook an egg.
# Subtask 2: Slice lettuce, tomato and bread.
# Subtask 3: Wash a plate.
# Subtask 4: Assemble the sandwich.
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
    # 1: Go to the Knife.
    GoToObject('Knife')
    # 2: Pick up the Knife.
    PickupObject('Knife')
    # 3: Go to the Lettuce.
    GoToObject('Lettuce')
    # 4: Slice the Lettuce.
    SliceObject('Lettuce')
    # 5: Go to the Tomato.
    GoToObject('Tomato')
    # 6: Slice the Tomato.
    SliceObject('Tomato')
    # 7: Go to the Bread.
    GoToObject('Bread')
    # 8: Slice the Bread.
    SliceObject('Bread')
    # 9: Go to the countertop.
    GoToObject('CounterTop')
    # 10: Put the Knife back on the CounterTop.
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
    # 1: Go to the bread slice.
    GoToObject('Bread')
    # 2: Pick up the bread slice.
    PickupObject('Bread')
    # 3: Go to the plate.
    GoToObject('Plate')
    # 4: Place a slice of bread on the plate.
    PutObject('Bread', 'Plate')
    # 5: Go to the lettuce.
    GoToObject('Lettuce')
    # 6: Pick up the lettuce.
    PickupObject('Lettuce')
    # 7: Go to the plate.
    GoToObject('Plate')
    # 8: Place a slice of lettuce on the plate.
    PutObject('Lettuce', 'Plate')
    # 9: Go to the tomato.
    GoToObject('Tomato')
    # 10: Pick up the tomato.
    PickupObject('Tomato')
    # 11: Go to the plate.
    GoToObject('Plate')
    # 12: Place a slice of tomato on the plate.
    PutObject('Tomato', 'Plate')
    # 13: Go to the egg.
    GoToObject('Egg')
    # 14: Pick up the egg.
    PickupObject('Egg')
    # 15: Go to the plate.
    GoToObject('Plate')
    # 16: Place a slice of egg on the plate.
    PutObject('Egg', 'Plate')
    # 17: Go to another bread slice.
    GoToObject('Bread')
    # 18: Pick up the bread slice.
    PickupObject('Bread')
    # 19: Go to the plate.
    GoToObject('Plate')
    # 20: Place another slice of bread on top of the plate.
    PutObject('Bread', 'Plate')

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



# EXAMPLE 3 -
