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
    GoToObject('BreadSliced')
    # 2: Pick up the sliced bread.
    PickupObjectSliced('BreadSliced')
    # 3: Go to the plate.
    GoToObject('Plate')
    # 4: Place a slice of bread on the plate.
    PutObjectSliced('BreadSliced', 'Plate')
    # 5: Go to the lettuce.
    GoToObject('LettuceSliced')
    # 6: Pick up the lettuce.
    PickupObjectSliced('LettuceSliced')
    # 7: Go to the plate.
    GoToObject('Plate')
    # 8: Place a slice of lettuce on the plate.
    PutObjectSliced('LettuceSliced', 'Plate')
    # 9: Go to the tomato.
    GoToObject('TomatoSliced')
    # 10: Pick up the tomato.
    PickupObjectSliced('TomatoSliced')
    # 11: Go to the plate.
    GoToObject('Plate')
    # 12: Place a slice of tomato on the plate.
    PutObjectSliced('TomatoSliced', 'Plate')
    # 13: Go to the egg.
    GoToObject('Egg')
    # 14: Pick up the egg.
    PickupObject('Egg')
    # 15: Go to the plate.
    GoToObject('Plate')
    # 16: Place a slice of egg on the plate.
    PutObject('Egg', 'Plate')