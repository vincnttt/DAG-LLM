# List of robots with different configurations

# ALL SKILLS - INF MASS (robot1, robot2, robot3, robot4)
robot1 = {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                                       'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

robot2 = {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                                       'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

robot3 = {'name': 'robot3', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                                       'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

robot4 = {'name': 'robot4', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                                       'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

# SPECIFIC SKILLS - INF MASS - NO ON + OFF
robot5 = {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject',
                                       'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

robot6 = {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject',
                                       'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

# SPECIFIC SKILLS - INF MASS - NO PICK + PUT
robot7 = {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                                       'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

robot8 = {'name': 'robot2', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                                       'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}

# SPECIFIC SKILLS - INF MASS - NO SLICE + BREAK + DROP + THROW
robot9 = {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'SwitchOn', 'SwitchOff',
                                       'PickupObject', 'PutObject', 'PushObject', 'PullObject'], 'mass': 100}

robot10 = {'name': 'robot1', 'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'SwitchOn', 'SwitchOff',
                                       'PickupObject', 'PutObject', 'PushObject', 'PullObject'], 'mass': 100}

robots = [robot1, robot2, robot3, robot4, robot5, robot6, robot7, robot8, robot9, robot10]