import math
import re
import shutil
import subprocess
import time
import threading
import cv2
import numpy as np
from ai2thor.controller import Controller
from scipy.spatial import distance
from typing import Tuple
from collections import deque
import random
import os
from glob import glob
from collections import deque, defaultdict



def closest_node(node, nodes, no_robot, clost_node_location):
    crps = []
    distances = distance.cdist([node], nodes)[0]
    dist_indices = np.argsort(np.array(distances))
    for i in range(no_robot):
        pos_index = dist_indices[(i * 5) + clost_node_location[i]]
        crps.append(nodes[pos_index])
    return crps


def distance_pts(p1: Tuple[float, float, float], p2: Tuple[float, float, float]):
    return ((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5


logs = []


def write_log(title, message):
    curr_path = os.path.dirname(__file__)
    with open(f"{curr_path}/log.txt", 'a') as f:
        f.write(f"\n")
        f.write(f"{title}: {message}")
        logs.append(f"{title}: {message}")


def generate_video():
    frame_rate = 5
    # input_path, prefix, char_id=0, image_synthesis=['normal'], frame_rate=5
    cur_path = os.path.dirname(__file__) + "/*/"
    for imgs_folder in glob(cur_path, recursive=False):
        view = imgs_folder.split('/')[-2]
        if not os.path.isdir(imgs_folder):
            print("The input path: {} you specified does not exist.".format(imgs_folder))
        else:
            command_set = ['ffmpeg', '-i',
                           '{}/img_%05d.png'.format(imgs_folder),
                           '-framerate', str(frame_rate),
                           '-pix_fmt', 'yuv420p',
                           '{}/video_{}.mp4'.format(os.path.dirname(__file__), view)]
            subprocess.call(command_set)

robots = [
    {'name': 'robot1',
     'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100},
    {'name': 'robot2',
     'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100},
    {'name': 'robot3',
     'skills': ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff',
                'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}
]

floor_no = 16

# Start run logs
curr_path = os.path.dirname(__file__)
with open(f"{curr_path}/log.txt", 'a') as f:
    f.write(f"\n\n\n")
    f.write(f"=========== LOGS ===========")

total_exec = 0
success_exec = 0

c = Controller(height=480, width=480)
c.reset("FloorPlan" + str(floor_no))
no_robot = len(robots)

# initialize n agents into the scene
multi_agent_event = c.step \
    (dict(action='Initialize', agentMode="default", snapGrid=False, gridSize=0.5, rotateStepDegrees=20, visibilityDistance=100, fieldOfView=90, agentCount=no_robot))

# add a top view camera
event = c.step(action="GetMapViewCameraProperties")
event = c.step(action="AddThirdPartyCamera", **event.metadata["actionReturn"])

# get reachabel positions
reachable_positions_ = c.step(action="GetReachablePositions").metadata["actionReturn"]
reachable_positions = positions_tuple = [(p["x"], p["y"], p["z"]) for p in reachable_positions_]

# randomize postions of the agents
for i in range (no_robot):
    init_pos = random.choice(reachable_positions_)
    c.step(dict(action="Teleport", position=init_pos, agentId=i))

objs = list([obj["objectId"] for obj in c.last_event.metadata["objects"]])
# print (objs)

# x = c.step(dict(action="RemoveFromScene", objectId='Lettuce|+01.11|+00.83|-01.43'))
# c.step({"action":"InitialRandomSpawn", "excludedReceptacles":["Microwave", "Pan", "Chair", "Plate", "Fridge", "Cabinet", "Drawer", "GarbageCan"]})
# c.step({"action":"InitialRandomSpawn", "excludedReceptacles":["Cabinet", "Drawer", "GarbageCan"]})

action_queue = []

task_over = False

recp_id = None

for i in range (no_robot):
    multi_agent_event = c.step(action="LookDown", degrees=35, agentId=i)
    # c.step(action="LookUp", degrees=30, 'agent_id':i)

def exec_actions():
    global total_exec, success_exec
    # delete if current output already exist
    cur_path = os.path.dirname(__file__) + "/*/"
    for x in glob(cur_path, recursive = True):
        shutil.rmtree (x)

    # create new folders to save the images from the agents
    for i in range(no_robot):
        folder_name = "agent_" + str( i +1)
        folder_path = os.path.dirname(__file__) + "/" + folder_name
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # create folder to store the top view images
    folder_name = "top_view"
    folder_path = os.path.dirname(__file__) + "/" + folder_name
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    img_counter = 0

    while not task_over:
        if len(action_queue) > 0:
            try:
                act = action_queue[0]
                if act['action'] == 'ObjectNavExpertAction':
                    multi_agent_event = c.step \
                        (dict(action=act['action'], position=act['position'], agentId=act['agent_id']))
                    next_action = multi_agent_event.metadata['actionReturn']

                    if next_action != None:
                        multi_agent_event = c.step(action=next_action, agentId=act['agent_id'], forceAction=True)

                elif act['action'] == 'MoveAhead':
                    multi_agent_event = c.step(action="MoveAhead", agentId=act['agent_id'])

                elif act['action'] == 'MoveBack':
                    multi_agent_event = c.step(action="MoveBack", agentId=act['agent_id'])

                elif act['action'] == 'RotateLeft':
                    multi_agent_event = c.step(action="RotateLeft", degrees=act['degrees'], agentId=act['agent_id'])

                elif act['action'] == 'RotateRight':
                    multi_agent_event = c.step(action="RotateRight", degrees=act['degrees'], agentId=act['agent_id'])

                elif act['action'] == 'PickupObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="PickupObject", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'PutObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="PutObject", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'ToggleObjectOn':
                    total_exec += 1
                    multi_agent_event = c.step(action="ToggleObjectOn", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'ToggleObjectOff':
                    total_exec += 1
                    multi_agent_event = c.step(action="ToggleObjectOff", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'OpenObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="OpenObject", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1


                elif act['action'] == 'CloseObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="CloseObject", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'SliceObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="SliceObject", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'ThrowObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="ThrowObject", moveMagnitude=7, agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'BreakObject':
                    total_exec += 1
                    multi_agent_event = c.step(action="BreakObject", objectId=act['objectId'], agentId=act['agent_id'], forceAction=True)
                    if multi_agent_event.metadata['errorMessage'] != "":
                        print (multi_agent_event.metadata['errorMessage'])
                        write_log("[ERROR]", multi_agent_event.metadata['errorMessage'])
                    else:
                        success_exec += 1

                elif act['action'] == 'Done':
                    multi_agent_event = c.step(action="Done")

            except Exception as e:
                print (e)
                write_log("[EXC]", e)

            for i ,e in enumerate(multi_agent_event.events):
                cv2.imshow('agent%s' % i, e.cv2img)
                f_name = os.path.dirname(__file__) + "/agent_" + str( i +1) + "/img_" + str(img_counter).zfill \
                    (5) + ".png"
                cv2.imwrite(f_name, e.cv2img)

            top_view_rgb = cv2.cvtColor(c.last_event.events[0].third_party_camera_frames[-1], cv2.COLOR_BGR2RGB)

            # cv2.imshow('Top View', top_view_rgb)
            # f_name = os.path.dirname(__file__) + "/top_view/img_" + str(img_counter).zfill(5) + ".png"
            # cv2.imwrite(f_name, top_view_rgb)
            # if cv2.waitKey(25) & 0xFF == ord('q'):
            #     break

            top_view_rgb = cv2.putText(top_view_rgb, f'{logs.pop(0) if logs else "WAIT"}', (20, 30),
                                       cv2.FONT_HERSHEY_SIMPLEX,
                                       1, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.imshow('Top View', top_view_rgb)
            f_name = os.path.dirname(__file__) + "/top_view/img_" + str(img_counter).zfill(5) + ".png"
            cv2.imwrite(f_name, top_view_rgb)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            img_counter += 1
            action_queue.pop(0)

actions_thread = threading.Thread(target=exec_actions)
actions_thread.start()

def GoToObject(robots, dest_obj):
    global recp_id

    # check if robots is a list
    if not isinstance(robots, list):
        # convert robot to a list
        robots = [robots]
    no_agents = len (robots)

    # robots distance to the goal
    dist_goals = [10.0] * len(robots)
    prev_dist_goals = [10.0] * len(robots)
    count_since_update = [0] * len(robots)
    clost_node_location = [0] * len(robots)

    # list of objects in the scene and their centers
    objs = list([obj["objectId"] for obj in c.last_event.metadata["objects"]])
    objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])
    if "|" in dest_obj:
        # obj alredy given
        dest_obj_id = dest_obj
        pos_arr = dest_obj_id.split("|")
        dest_obj_center = {'x': float(pos_arr[1]), 'y': float(pos_arr[2]), 'z': float(pos_arr[3])}
    else:
        for idx, obj in enumerate(objs):

            match = re.match(dest_obj, obj)
            if match is not None:
                dest_obj_id = obj
                dest_obj_center = objs_center[idx]
                if dest_obj_center != {'x': 0.0, 'y': 0.0, 'z': 0.0}:
                    break # find the first instance

    print ("Going to ", dest_obj_id, dest_obj_center)
    write_log("[Going To]", f"{dest_obj_id} {dest_obj_center}")

    dest_obj_pos = [dest_obj_center['x'], dest_obj_center['y'], dest_obj_center['z']]

    # closest reachable position for each robot
    # all robots cannot reach the same spot
    # differt close points needs to be found for each robot
    crp = closest_node(dest_obj_pos, reachable_positions, no_agents, clost_node_location)

    goal_thresh = 0.25
    # at least one robot is far away from the goal

    while all(d > goal_thresh for d in dist_goals):
        for ia, robot in enumerate(robots):
            robot_name = robot['name']
            agent_id = int(robot_name[-1]) - 1

            # get the pose of robot
            metadata = c.last_event.events[agent_id].metadata
            location = {
                "x": metadata["agent"]["position"]["x"],
                "y": metadata["agent"]["position"]["y"],
                "z": metadata["agent"]["position"]["z"],
                "rotation": metadata["agent"]["rotation"]["y"],
                "horizon": metadata["agent"]["cameraHorizon"]}

            prev_dist_goals[ia] = dist_goals[ia] # store the previous distance to goal
            dist_goals[ia] = distance_pts([location['x'], location['y'], location['z']], crp[ia])

            dist_del = abs(dist_goals[ia] - prev_dist_goals[ia])
            # print (ia, "Dist to Goal: ", dist_goals[ia], dist_del, clost_node_location[ia])
            if dist_del < 0.2:
                # robot did not move
                count_since_update[ia] += 1
            else:
                # robot moving
                count_since_update[ia] = 0

            if count_since_update[ia] < 8:
                action_queue.append \
                    ({'action' :'ObjectNavExpertAction', 'position' :dict(x=crp[ia][0], y=crp[ia][1], z=crp[ia][2]), 'agent_id' :agent_id})
            else:
                # updating goal
                clost_node_location[ia] += 1
                count_since_update[ia] = 0
                crp = closest_node(dest_obj_pos, reachable_positions, no_agents, clost_node_location)

            time.sleep(0.5)

    # align the robot once goal is reached
    # compute angle between robot heading and object
    metadata = c.last_event.events[agent_id].metadata
    robot_location = {
        "x": metadata["agent"]["position"]["x"],
        "y": metadata["agent"]["position"]["y"],
        "z": metadata["agent"]["position"]["z"],
        "rotation": metadata["agent"]["rotation"]["y"],
        "horizon": metadata["agent"]["cameraHorizon"]}

    robot_object_vec = [dest_obj_pos[0] -robot_location['x'], dest_obj_pos[2] - robot_location['z']]
    y_axis = [0, 1]
    unit_y = y_axis / np.linalg.norm(y_axis)
    unit_vector = robot_object_vec / np.linalg.norm(robot_object_vec)

    angle = math.atan2(np.linalg.det([unit_vector, unit_y]), np.dot(unit_vector, unit_y))
    angle = 360 * angle / (2 * np.pi)
    angle = (angle + 360) % 360
    rot_angle = angle - robot_location['rotation']

    if rot_angle > 0:
        action_queue.append({'action': 'RotateRight', 'degrees': abs(rot_angle), 'agent_id': agent_id})
    else:
        action_queue.append({'action': 'RotateLeft', 'degrees': abs(rot_angle), 'agent_id': agent_id})

    print("Reached: ", dest_obj)
    write_log("[Reached]", dest_obj)
    if dest_obj == "Cabinet" or dest_obj == "Fridge" or dest_obj == "CounterTop":
        recp_id = dest_obj_id


def GoToSlicedObject(robots, dest_obj):
    global recp_id

    # check if robots is a list
    if not isinstance(robots, list):
        # convert robot to a list
        robots = [robots]
    no_agents = len (robots)

    # robots distance to the goal
    dist_goals = [10.0] * len(robots)
    prev_dist_goals = [10.0] * len(robots)
    count_since_update = [0] * len(robots)
    clost_node_location = [0] * len(robots)

    # list of objects in the scene and their centers
    objs = list([obj["objectId"] for obj in c.last_event.metadata["objects"]])
    objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])
    if "|" in dest_obj:
        # obj alredy given
        dest_obj_id = dest_obj
        pos_arr = dest_obj_id.split("|")
        dest_obj_center = {'x': float(pos_arr[1]), 'y': float(pos_arr[2]), 'z': float(pos_arr[3])}
    else:
        for idx, obj in enumerate(objs):

            # match = re.match(dest_obj, obj)
            match = re.match(dest_obj + "_1", obj.rsplit('|', 1)[-1])
            if match is not None:
                dest_obj_id = obj
                dest_obj_center = objs_center[idx]
                if dest_obj_center != {'x': 0.0, 'y': 0.0, 'z': 0.0}:
                    break # find the first instance

    print ("Going to ", dest_obj_id, dest_obj_center)
    write_log("[Going To]", f"{dest_obj_id} {dest_obj_center}")

    dest_obj_pos = [dest_obj_center['x'], dest_obj_center['y'], dest_obj_center['z']]

    # closest reachable position for each robot
    # all robots cannot reach the same spot
    # differt close points needs to be found for each robot
    crp = closest_node(dest_obj_pos, reachable_positions, no_agents, clost_node_location)

    goal_thresh = 0.25
    # at least one robot is far away from the goal

    while all(d > goal_thresh for d in dist_goals):
        for ia, robot in enumerate(robots):
            robot_name = robot['name']
            agent_id = int(robot_name[-1]) - 1

            # get the pose of robot
            metadata = c.last_event.events[agent_id].metadata
            location = {
                "x": metadata["agent"]["position"]["x"],
                "y": metadata["agent"]["position"]["y"],
                "z": metadata["agent"]["position"]["z"],
                "rotation": metadata["agent"]["rotation"]["y"],
                "horizon": metadata["agent"]["cameraHorizon"]}

            prev_dist_goals[ia] = dist_goals[ia] # store the previous distance to goal
            dist_goals[ia] = distance_pts([location['x'], location['y'], location['z']], crp[ia])

            dist_del = abs(dist_goals[ia] - prev_dist_goals[ia])
            # print (ia, "Dist to Goal: ", dist_goals[ia], dist_del, clost_node_location[ia])
            if dist_del < 0.2:
                # robot did not move
                count_since_update[ia] += 1
            else:
                # robot moving
                count_since_update[ia] = 0

            if count_since_update[ia] < 8:
                action_queue.append \
                    ({'action' :'ObjectNavExpertAction', 'position' :dict(x=crp[ia][0], y=crp[ia][1], z=crp[ia][2]), 'agent_id' :agent_id})
            else:
                # updating goal
                clost_node_location[ia] += 1
                count_since_update[ia] = 0
                crp = closest_node(dest_obj_pos, reachable_positions, no_agents, clost_node_location)

            time.sleep(0.5)

    # align the robot once goal is reached
    # compute angle between robot heading and object
    metadata = c.last_event.events[agent_id].metadata
    robot_location = {
        "x": metadata["agent"]["position"]["x"],
        "y": metadata["agent"]["position"]["y"],
        "z": metadata["agent"]["position"]["z"],
        "rotation": metadata["agent"]["rotation"]["y"],
        "horizon": metadata["agent"]["cameraHorizon"]}

    robot_object_vec = [dest_obj_pos[0] -robot_location['x'], dest_obj_pos[2] - robot_location['z']]
    y_axis = [0, 1]
    unit_y = y_axis / np.linalg.norm(y_axis)
    unit_vector = robot_object_vec / np.linalg.norm(robot_object_vec)

    angle = math.atan2(np.linalg.det([unit_vector, unit_y]), np.dot(unit_vector, unit_y))
    angle = 360 * angle / (2 * np.pi)
    angle = (angle + 360) % 360
    rot_angle = angle - robot_location['rotation']

    if rot_angle > 0:
        action_queue.append({'action': 'RotateRight', 'degrees': abs(rot_angle), 'agent_id': agent_id})
    else:
        action_queue.append({'action': 'RotateLeft', 'degrees': abs(rot_angle), 'agent_id': agent_id})

    print("Reached: ", dest_obj)
    write_log("[Reached]", dest_obj)
    if dest_obj == "Cabinet" or dest_obj == "Fridge" or dest_obj == "CounterTop":
        recp_id = dest_obj_id


def CleanArea(robots):
    global recp_id

    if not isinstance(robots, list):
        robots = [robots]
    no_agents = len(robots)

    dist_goals = []
    prev_dist_goals = [10.0] * len(robots)
    count_since_update = [0] * len(robots)
    closest_node_location = [0] * len(robots)

    goal_tresh = 0.35

    while all(d > goal_tresh for d in dist_goals):
        for ia, robot in enumerate(robots):
            robot_name = robot['name']
            agent_id = int(robot_name[-1]) - 1

            metadata = c.last_event.events[agent_id].metadata
            location = {
                "x": metadata["agent"]["position"]["x"],
                "y": metadata["agent"]["position"]["y"],
                "z": metadata["agent"]["position"]["z"],
                "rotation": metadata["agent"]["rotation"]["y"],
                "horizon": metadata["agent"]["cameraHorizon"]}

            prev_dist_goals[ia] = dist_goals[ia]
            dist_goals[ia] = distance_pts()


def PickupObject(robots, pick_obj):
    if not isinstance(robots, list):
        # convert robot to a list
        robots = [robots]
    no_agents = len(robots)
    # robots distance to the goal
    for idx in range(no_agents):
        print("Picking: ", pick_obj)
        write_log("[Picking]", pick_obj)

        robot = robots[idx]
        robot_name = robot['name']
        agent_id = int(robot_name[-1]) - 1
        # list of objects in the scene and their centers
        objs = list([obj["objectId"] for obj in c.last_event.metadata["objects"]])
        objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])

        for idx, obj in enumerate(objs):
            match = re.match(pick_obj, obj)
            if match is not None:
                pick_obj_id = obj
                dest_obj_center = objs_center[idx]
                if dest_obj_center != {'x': 0.0, 'y': 0.0, 'z': 0.0}:
                    break  # find the first instance
        # GoToObject(robot, pick_obj_id)
        # time.sleep(1)
        print("Picking Up ", pick_obj_id, dest_obj_center)
        write_log("[Picking Up]", f"{pick_obj_id} {dest_obj_center}")

        action_queue.append({'action': 'PickupObject', 'objectId': pick_obj_id, 'agent_id': agent_id})
        time.sleep(1)


def PickupSlicedObject(robots, pick_obj):
    if not isinstance(robots, list):
        # convert robot to a list
        robots = [robots]
    no_agents = len(robots)
    # robots distance to the goal
    for idx in range(no_agents):
        print("Picking Sliced: ", pick_obj)
        write_log("[Picking Sliced]", pick_obj)

        robot = robots[idx]
        robot_name = robot['name']
        agent_id = int(robot_name[-1]) - 1
        objs = list([obj["objectId"] for obj in c.last_event.metadata["objects"]])
        objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])

        for idx, obj in enumerate(objs):
            match = re.match(pick_obj + "_1", obj.rsplit('|', 1)[-1])
            if match is not None:
                pick_obj_id = obj
                dest_obj_center = objs_center[idx]
                if dest_obj_center != {'x': 0.0, 'y': 0.0, 'z': 0.0}:
                    break  # find the first instance

        print("Picking Up Sliced ", pick_obj_id, dest_obj_center)
        write_log("[Picking Up Sliced]", f"{pick_obj_id} {dest_obj_center}")

        action_queue.append({'action': 'PickupObject', 'objectId': pick_obj_id, 'agent_id': agent_id})
        time.sleep(1)


def PutObject(robot, put_obj, recp):
    print("Putting: ", put_obj)
    write_log("[Putting]", put_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))
    objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])
    objs_dists = list([obj["distance"] for obj in c.last_event.metadata["objects"]])

    metadata = c.last_event.events[agent_id].metadata
    robot_location = [metadata["agent"]["position"]["x"], metadata["agent"]["position"]["y"],
                      metadata["agent"]["position"]["z"]]
    dist_to_recp = 9999999  # distance b/w robot and the recp obj
    for idx, obj in enumerate(objs):
        match = re.match(recp, obj)
        if match is not None:
            dist = objs_dists[idx]
            if dist < dist_to_recp:
                recp_obj_id = obj
                dest_obj_center = objs_center[idx]
                dist_to_recp = dist

    global recp_id
    # if recp_id is not None:
    #     recp_obj_id = recp_id
    # GoToObject(robot, recp_obj_id)
    # time.sleep(1)
    print("Putting In: ", recp_obj_id, dest_obj_center)
    write_log("[Putting In]", f"{recp_obj_id} {dest_obj_center}")

    action_queue.append({'action': 'PutObject', 'objectId': recp_obj_id, 'agent_id': agent_id})
    time.sleep(1)


def PutSlicedObject(robot, put_obj, recp):
    print("Putting Sliced: ", put_obj)
    write_log("[Putting Sliced]", put_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))
    objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])
    objs_dists = list([obj["distance"] for obj in c.last_event.metadata["objects"]])

    metadata = c.last_event.events[agent_id].metadata
    robot_location = [metadata["agent"]["position"]["x"], metadata["agent"]["position"]["y"],
                      metadata["agent"]["position"]["z"]]
    dist_to_recp = 9999999  # distance b/w robot and the recp obj
    for idx, obj in enumerate(objs):
        match = re.match(recp.rsplit('|', 1)[-1], obj + "_1")
        if match is not None:
            dist = objs_dists[idx]
            if dist < dist_to_recp:
                recp_obj_id = obj
                dest_obj_center = objs_center[idx]
                dist_to_recp = dist

    global recp_id
    # if recp_id is not None:
    #     recp_obj_id = recp_id
    # GoToObject(robot, recp_obj_id)
    # time.sleep(1)
    print("Putting In Sliced: ", recp_obj_id, dest_obj_center)
    write_log("[Putting In Sliced]", f"{recp_obj_id} {dest_obj_center}")

    action_queue.append({'action': 'PutObject', 'objectId': recp_obj_id, 'agent_id': agent_id})
    time.sleep(1)


def SwitchOn(robot, sw_obj):
    print("Switching On: ", sw_obj)
    write_log("[Switching On]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    # turn on all stove burner
    if sw_obj == "StoveKnob":
        for obj in objs:
            match = re.match(sw_obj, obj)
            if match is not None:
                sw_obj_id = obj
                GoToObject(robot, sw_obj_id)
                # time.sleep(1)
                action_queue.append({'action': 'ToggleObjectOn', 'objectId': sw_obj_id, 'agent_id': agent_id})
                time.sleep(0.1)

    # all objects apart from Stove Burner
    else:
        for obj in objs:
            match = re.match(sw_obj, obj)
            if match is not None:
                sw_obj_id = obj
                break  # find the first instance
        GoToObject(robot, sw_obj_id)
        time.sleep(1)
        action_queue.append({'action': 'ToggleObjectOn', 'objectId': sw_obj_id, 'agent_id': agent_id})
        time.sleep(1)


def SwitchOff(robot, sw_obj):
    print("Switching Off: ", sw_obj)
    write_log("[Switching Off]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    # turn on all stove burner
    if sw_obj == "StoveKnob":
        for obj in objs:
            match = re.match(sw_obj, obj)
            if match is not None:
                sw_obj_id = obj
                action_queue.append({'action': 'ToggleObjectOff', 'objectId': sw_obj_id, 'agent_id': agent_id})
                time.sleep(0.1)

    # all objects apart from Stove Burner
    else:
        for obj in objs:
            match = re.match(sw_obj, obj)
            if match is not None:
                sw_obj_id = obj
                break  # find the first instance
        GoToObject(robot, sw_obj_id)
        time.sleep(1)
        action_queue.append({'action': 'ToggleObjectOff', 'objectId': sw_obj_id, 'agent_id': agent_id})
        time.sleep(1)


def OpenObject(robot, sw_obj):
    print("Opening: ", sw_obj)
    write_log("[Opening]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    for obj in objs:
        match = re.match(sw_obj, obj)
        if match is not None:
            sw_obj_id = obj
            break  # find the first instance

    global recp_id
    if recp_id is not None:
        sw_obj_id = recp_id

    GoToObject(robot, sw_obj_id)
    time.sleep(1)
    action_queue.append({'action': 'OpenObject', 'objectId': sw_obj_id, 'agent_id': agent_id})
    time.sleep(1)


def CloseObject(robot, sw_obj):
    print("Closing: ", sw_obj)
    write_log("[Closing]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    for obj in objs:
        match = re.match(sw_obj, obj)
        if match is not None:
            sw_obj_id = obj
            break  # find the first instance

    global recp_id
    if recp_id is not None:
        sw_obj_id = recp_id

    GoToObject(robot, sw_obj_id)
    time.sleep(1)

    action_queue.append({'action': 'CloseObject', 'objectId': sw_obj_id, 'agent_id': agent_id})

    if recp_id is not None:
        recp_id = None
    time.sleep(1)


def BreakObject(robot, sw_obj):
    print("Breaking: ", sw_obj)
    write_log("[Breaking]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    for obj in objs:
        match = re.match(sw_obj, obj)
        if match is not None:
            sw_obj_id = obj
            break  # find the first instance
    GoToObject(robot, sw_obj_id)
    time.sleep(1)
    action_queue.append({'action': 'BreakObject', 'objectId': sw_obj_id, 'agent_id': agent_id})
    time.sleep(1)


def SliceObject(robot, sw_obj):
    print("Slicing: ", sw_obj)
    write_log("[Slicing]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    for obj in objs:
        match = re.match(sw_obj, obj)
        if match is not None:
            sw_obj_id = obj
            break  # find the first instance
    GoToObject(robot, sw_obj_id)
    time.sleep(1)
    action_queue.append({'action': 'SliceObject', 'objectId': sw_obj_id, 'agent_id': agent_id})
    time.sleep(1)


def CleanObject(robot, sw_obj):
    print("Cleaning: ", sw_obj)
    write_log("[Cleaning]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    for obj in objs:
        match = re.match(sw_obj, obj)
        if match is not None:
            sw_obj_id = obj
            break  # find the first instance
    GoToObject(robot, sw_obj_id)
    time.sleep(1)
    action_queue.append({'action': 'CleanObject', 'objectId': sw_obj_id, 'agent_id': agent_id})
    time.sleep(1)


def ThrowObject(robot, sw_obj):
    print("Throwing: ", sw_obj)
    write_log("[Throwing]", sw_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))

    for obj in objs:
        match = re.match(sw_obj, obj)
        if match is not None:
            sw_obj_id = obj
            break  # find the first instance

    action_queue.append({'action': 'ThrowObject', 'objectId': sw_obj_id, 'agent_id': agent_id})
    time.sleep(1)


### V1
# def execute_tasks_in_parallel(tasks, dependencies, robot_task_map):
#     # Step 1: Build graph and in-degrees
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0  # Initialize if not already present
#
#     # Step 2: Calculate task levels
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     task_level = {}
#     level = 0
#
#     while queue:
#         size = len(queue)
#         for _ in range(size):
#             current = queue.popleft()
#             task_level[current] = level
#             for neighbor in graph[current]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     queue.append(neighbor)
#         level += 1  # Increment level after processing one level of tasks
#
#     # Group tasks by level for parallel execution
#     level_tasks = defaultdict(list)
#     for task, lvl in task_level.items():
#         level_tasks[lvl].append(task)
#
#     # Step 3: Execute tasks using threads
#     # def run_task(task):
#     #     robot = next(robot for robot, tasks in robot_task_map.items() if task in tasks)
#     #     print(f"Starting task {task} on {robot} index ")
#     #     # time.sleep(task_durations[task])  # Simulate task duration
#     #     print(f"Finished task {task} on {robot}")
#     #
#     # for lvl in sorted(level_tasks.keys()):
#     #     threads = []
#     #     print(f"Executing level {lvl} tasks in parallel: {level_tasks[lvl]}")
#     #     for task in level_tasks[lvl]:
#     #         print(run_task)
#     #         print(task)
#     #         # thread = threading.Thread(target=run_task, args=(task,))
#     #         thread = threading.Thread(target=run_task, args=(robots[],))
#     #         threads.append(thread)
#     #         thread.start()
#     #     for thread in threads:
#     #         thread.join()  # Wait for all tasks in the level to complete
#     #     print(f"Completed all level {lvl} tasks.\n")
#
#     def run_task(robot, task):
#         print(f"Starting task {task} on {robot}")
#         # time.sleep(task_durations[task])  # Simulate task duration
#         print(f"Finished task {task} on {robot}")
#
#     # Updated threading.Thread call inside the loop
#     for lvl in sorted(level_tasks.keys()):
#         threads = []
#         print(f"Executing level {lvl} tasks in parallel: {level_tasks[lvl]}")
#         for task in level_tasks[lvl]:
#             # Find the robot assigned to the current task
#             robot = next(robot for robot, tasks in robot_task_map.items() if task in tasks)
#             thread = threading.Thread(target=globals()[task], args=(robots[robot],))
#             threads.append(thread)
#             thread.start()
#         for thread in threads:
#             thread.join()  # Wait for all tasks in the level to complete
#         print(f"Completed all level {lvl} tasks.\n")


### V2
# def execute_tasks_with_robot_availability(tasks, dependencies, robot_task_map):
#     # Step 1: Build graph and in-degrees
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0  # Initialize if not already present
#
#     # Step 2: Calculate task levels
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     task_level = {}
#     level = 0
#
#     while queue:
#         size = len(queue)
#         for _ in range(size):
#             current = queue.popleft()
#             task_level[current] = level
#             for neighbor in graph[current]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     queue.append(neighbor)
#         level += 1  # Increment level after processing one level of tasks
#
#     # Group tasks by level for parallel execution
#     level_tasks = defaultdict(list)
#     for task, lvl in task_level.items():
#         level_tasks[lvl].append(task)
#
#     # Step 3: Execute tasks with robot availability tracking
#     robot_availability = {robot: 0 for robot in robot_task_map}  # Tracks when each robot is free
#     lock = threading.Lock()  # To ensure thread-safe updates to robot_availability
#
#     def run_task(robot, task):
#         with lock:
#             robot = next(robot for robot, tasks in robot_task_map.items() if task in tasks)
#             print(f"Starting task {task} on {robot}")
#         time.sleep(task_durations[task])  # Simulate task duration
#         with lock:
#             print(f"Finished task {task} on {robot}")
#             robot_availability[robot] = time.time()  # Mark robot as free
#
#     for lvl in sorted(level_tasks.keys()):
#         threads = []
#         print(f"Executing level {lvl} tasks in parallel: {level_tasks[lvl]}")
#         for task in level_tasks[lvl]:
#             # Find the first available robot that can handle this task
#             while True:
#                 with lock:
#                     current_time = time.time()
#                     available_robots = [robot for robot, free_time in robot_availability.items()
#                                         if free_time <= current_time and task in robot_task_map[robot]]
#                 if available_robots:
#                     chosen_robot = available_robots[0]  # Pick the first available robot
#                     robot_availability[chosen_robot] = current_time + task_durations[task]  # Update availability
#                     # thread = threading.Thread(target=run_task, args=(chosen_robot, task))
#                     thread = threading.Thread(target=run_task, args=(chosen_robot[],))
#                     threads.append(thread)
#                     thread.start()
#                     break
#                 else:
#                     time.sleep(0.1)  # Wait for robots to become available
#         for thread in threads:
#             thread.join()  # Wait for all tasks in the level to complete
#         print(f"Completed all level {lvl} tasks.\n")



### TEST CASES 1
def turn_off_lights(robot):
    # 0: Subtask 1: Turn off the lights.
    # 1: Go to the light switch.
    GoToObject(robot, 'LightSwitch')
    # 2: Turn off the lights.
    SwitchOff(robot, 'LightSwitch')

def turn_off_floor_lamp(robot):
    # 0: Subtask 2: Turn off the floor lamp.
    # 1: Go to the floor lamp.
    GoToObject(robot, 'FloorLamp')
    # 2: Turn off the floor lamp.
    SwitchOff(robot, 'FloorLamp')
#
# subtasks = ["turn_off_lights", "turn_off_floor_lamp"]
#
# dependencies = []
#
# qualified_robot = {
#     "turn_off_lights": [0,1],    # Subtask slice_bread can be done by Robot 1 and Robot 2
#     "turn_off_floor_lamp": [0,1],    # Subtask toast_bread can be done by Robot 1 and Robot 2
# }

### TEST CASES 1
# def cook_egg(robot):
#     GoToObject(robot, 'Egg')
#     PickupObject(robot, 'Egg')
#     GoToObject(robot, 'Pan')
#     PutObject(robot, 'Egg', 'Pan')
#     BreakObject(robot, 'Egg')
#     PickupObject(robot, 'Pan')
#     GoToObject(robot, 'StoveBurner')
#     PutObject(robot, 'Pan', 'StoveBurner')
#     SwitchOn(robot, 'StoveKnob')
#     time.sleep(5)
#     SwitchOff(robot, 'StoveKnob')
#
# def serve_egg(robot):
#     GoToObject(robot, 'Egg')
#     PickupObject(robot, 'Egg')
#     GoToObject(robot, 'Plate')
#     PutObject(robot, 'Egg', 'Plate')
#
# subtasks = ["cook_egg", "serve_egg"]
#
# dependencies = [("cook_egg", "serve_egg")]
#
# qualified_robot = {
#     "cook_egg": [0,1],
#     "serve_egg": [0,1],
# }

# def put_pen_to_drawer(robot):
#     GoToObject(robot, 'Pen')
#     PickupObject(robot, 'Pen')
#     OpenObject(robot, 'Drawer')
#     PutObject(robot, 'Pen', 'Drawer')
#     CloseObject(robot, 'Drawer')
#
# subtasks = ["turn_off_lights", "turn_off_floor_lamp", "put_pen_to_drawer"]
#
# dependencies = [
#     ("turn_off_lights", "put_pen_to_drawer"),
#     ("turn_off_floor_lamp", "put_pen_to_drawer"),
# ]
#
# qualified_robot = {
#     "turn_off_lights": [0,1],    # Subtask slice_bread can be done by Robot 1 and Robot 2
#     "turn_off_floor_lamp": [0,1],    # Subtask toast_bread can be done by Robot 1 and Robot 2
#     "put_pen_to_drawer": [0,1]      # Subtask serve_toast_on_plate can be done by Robot 1 and Robot 2
# }

# def put_vegetables_to_fridge(robot):
#     GoToObject(robot, 'Mug')
#     PickupObject(robot, 'Mug')
#     GoToObject(robot, 'CoffeeMachine')
#     PutObject(robot, 'Mug', 'CoffeeMachine')
#     SwitchOn(robot, 'CoffeeMachine')
#     time.sleep(5)
#     SwitchOff(robot, 'CoffeeMachine')
#     PickupObject(robot, 'Mug')
#     GoToObject(robot, 'CounterTop')
#     PutObject(robot, 'Mug', 'CounterTop')
#
#
# put_vegetables_to_fridge(robots[0])

### CUSTOM task_duration - V1, V2 ONLY, NOT IMPLEMENTED YET ON V3
# task_durations = {
#     "turn_off_lights": 2,  # Simulate task 1 takes 2 seconds
#     "turn_off_floor_lamp": 3,  # Simulate task 2 takes 3 seconds
#     "put_pen_to_drawer": 2,  # Simulate task 3 takes 2 seconds
# }


def slice_bread(robots):
    GoToObject(robots, 'Knife')
    PickupObject(robots, 'Knife')
    GoToObject(robots, 'Bread')
    SliceObject(robots, 'Bread')
    GoToObject(robots, 'CounterTop')
    PutObject(robots, 'Knife', 'CounterTop')

def toast_bread(robots):
    GoToSlicedObject(robots, 'BreadSliced')
    PickupSlicedObject(robots, 'BreadSliced')
    GoToObject(robots, 'Toaster')
    PutSlicedObject(robots, 'BreadSliced', 'Toaster')
    SwitchOn(robots, 'Toaster')
    time.sleep(5)
    SwitchOff(robots, 'Toaster')

def serve_toast_on_plate(robots):
    GoToObject(robots, 'Toaster')
    PickupSlicedObject(robots, 'BreadSliced')
    GoToObject(robots, 'Plate')
    PutSlicedObject(robots, 'BreadSliced', 'Plate')

def make_a_coffee(robots):
    GoToObject(robots, 'Mug')
    PickupObject(robots, 'Mug')
    GoToObject(robots, 'CoffeeMachine')
    PutObject(robots, 'Mug', 'CoffeeMachine')
    SwitchOn(robots, 'CoffeeMachine')
    time.sleep(5)
    SwitchOff(robots, 'CoffeeMachine')
    PickupObject(robots, 'Mug')
    GoToObject(robots, 'CounterTop')
    PutObject(robots, 'Mug', 'CounterTop')

def make_salad(robots):
    GoToObject(robots, 'Knife')
    PickupObject(robots, 'Knife')
    GoToObject(robots, 'Lettuce')
    SliceObject(robots, 'Lettuce')
    GoToObject(robots, 'Tomato')
    SliceObject(robots, 'Tomato')
    # GoToObject(robots, 'Cucumber')
    # SliceObject(robots, 'Cucumber')
    GoToObject(robots, 'Plate')
    PickupSlicedObject(robots, 'LettuceSliced')
    PutSlicedObject(robots, 'LettuceSliced', 'Plate')
    PickupSlicedObject(robots, 'TomatoSliced')
    PutSlicedObject(robots, 'TomatoSliced', 'Plate')
    # PutSlicedObject(robots, 'CucumberSliced', 'Plate')
    GoToObject(robots, 'CounterTop')
    PutObject(robots, 'Knife', 'CounterTop')

def throw_egg_to_trash(robots):
    GoToObject(robots, 'Egg')
    PickupObject(robots, 'Egg')
    GoToObject(robots, 'GarbageCan')
    ThrowObject(robots, 'Egg')

def turn_off_light(robots):
    GoToObject(robots, 'LightSwitch')
    SwitchOff(robots, 'LightSwitch')

# Initialize subtasks
subtasks = [
    "slice_bread", "toast_bread", "serve_toast_on_plate",
    "make_a_coffee", "make_salad", "throw_egg_to_trash", "turn_off_light"
]

# DAG dependencies
dependencies = [
    ("slice_bread", "toast_bread"),
    ("toast_bread", "serve_toast_on_plate")
]

# Qualified robots for each subtask
qualified_robot = {
    "slice_bread": [0, 1, 2],
    "toast_bread": [0, 1, 2],
    "serve_toast_on_plate": [0, 1, 2],
    "make_a_coffee": [0, 1, 2],
    "make_salad": [0, 1, 2],
    "throw_egg_to_trash": [0, 1, 2],
    "turn_off_light": [0, 1, 2]
}



def build_graph(dependencies):
    """Build task dependency graph and calculate in-degrees."""
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for src, dst in dependencies:
        graph[src].append(dst)
        in_degree[dst] += 1

    for task in subtasks:
        if task not in in_degree:
            in_degree[task] = 0  # Tasks with no incoming edges

    return graph, in_degree


def assign_tasks_dynamically(graph, in_degree, independent_tasks, qualified_robot):
    """Dynamically assign tasks to robots while respecting dependencies."""
    # Queue of ready tasks (tasks with in-degree 0)
    ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])

    # Queue for independent tasks
    independent_queue = deque(independent_tasks)

    # Track completed tasks
    completed_tasks = set()

    # Robot availability tracking
    robot_status = {i: True for i in range(len(robots))}  # True means available
    robot_locks = {i: threading.Lock() for i in range(len(robots))}
    task_assignment_lock = threading.Lock()  # Synchronize task assignment

    # Task execution function
    def execute_task(task, robot_idx):
        with robot_locks[robot_idx]:
            # Mark robot as busy
            robot_status[robot_idx] = False
            # print(f"Task '{task}' is being executed by {robot_idx}")
            # time.sleep(1)  # Simulate task duration
            # print(f"Task '{task}' completed by {robot_idx}")
            print(f"Task {task} is being executed by robot{robot_idx}")
            globals()[task](robots[robot_idx])
            # Mark robot as available and task as completed
            robot_status[robot_idx] = True
            completed_tasks.add(task)

    # Dynamic task assignment
    threads = []
    while ready_queue or independent_queue:
        # Synchronize task assignment
        with task_assignment_lock:
            # Process dependent tasks first
            task_batch = list(ready_queue)
            ready_queue.clear()

            for task in task_batch:
                if task in completed_tasks:  # Skip already completed tasks
                    continue
                assigned = False
                for robot_idx, available in robot_status.items():
                    if available and robot_idx in qualified_robot[task]:
                        thread = threading.Thread(target=execute_task, args=(task, robot_idx))
                        threads.append(thread)
                        thread.start()
                        assigned = True
                        break
                if not assigned:
                    ready_queue.append(task)  # Re-enqueue if no robot available

            # Process independent tasks if robots are available
            independent_batch = list(independent_queue)
            independent_queue.clear()

            for task in independent_batch:
                if task in completed_tasks:  # Skip already completed tasks
                    continue
                assigned = False
                for robot_idx, available in robot_status.items():
                    if available and robot_idx in qualified_robot[task]:
                        thread = threading.Thread(target=execute_task, args=(task, robot_idx))
                        threads.append(thread)
                        thread.start()
                        assigned = True
                        break
                if not assigned:
                    independent_queue.append(task)  # Re-enqueue if no robot available

        # Wait for threads to finish
        for thread in threads:
            thread.join()

        # Update dependencies for dependent tasks
        for task in task_batch:
            for neighbor in graph[task]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0 and neighbor not in completed_tasks:
                    ready_queue.append(neighbor)


# Build the task graph and calculate in-degrees
graph, in_degree = build_graph(dependencies)

# Separate dependent and independent tasks
dependent_tasks = set(graph.keys()).union(*graph.values())
independent_tasks = set(subtasks) - dependent_tasks

# Assign tasks dynamically
print("\nExecuting Tasks:")
assign_tasks_dynamically(graph, in_degree, independent_tasks, qualified_robot)


### V4.1
# def build_graph(dependencies):
#     """Build task dependency graph and calculate in-degrees."""
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for src, dst in dependencies:
#         graph[src].append(dst)
#         in_degree[dst] += 1
#
#     for task in subtasks:
#         if task not in in_degree:
#             in_degree[task] = 0  # Tasks with no incoming edges
#
#     return graph, in_degree
#
#
# def assign_tasks_dynamically(graph, in_degree, independent_tasks, qualified_robot):
#     """Dynamically assign tasks to robots while respecting dependencies."""
#     # Queue of ready tasks (tasks with in-degree 0)
#     ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])
#
#     # Queue for independent tasks
#     independent_queue = deque(independent_tasks)
#
#     # Robot availability tracking
#     robot_status = {i: True for i in range(len(robots))}  # True means available
#     robot_locks = {i: threading.Lock() for i in range(len(robots))}
#
#     # Task execution function
#     def execute_task(task, robot_idx):
#         with robot_locks[robot_idx]:
#             # Mark robot as busy
#             robot_status[robot_idx] = False
#             # print(f"Task {task} is being executed by robot{robot_idx}")
#             # globals()[task](robots[robot_idx])
#             print(f"Task '{task}' is being executed by {robot_idx}")
#             time.sleep(1)  # Simulate task duration
#             print(f"Task '{task}' completed by {robot_idx}")
#             # Mark robot as available
#             robot_status[robot_idx] = True
#
#     # Dynamic task assignment
#     threads = []
#     while ready_queue or independent_queue:
#         # Process dependent tasks first
#         task_batch = list(ready_queue)
#         ready_queue.clear()
#
#         for task in task_batch:
#             assigned = False
#             for robot_idx, available in robot_status.items():
#                 if available and robot_idx in qualified_robot[task]:
#                     thread = threading.Thread(target=execute_task, args=(task, robot_idx))
#                     threads.append(thread)
#                     thread.start()
#                     assigned = True
#                     break
#             if not assigned:
#                 ready_queue.append(task)  # Re-enqueue if no robot available
#
#         # Process independent tasks if robots are available
#         independent_batch = list(independent_queue)
#         independent_queue.clear()
#
#         for task in independent_batch:
#             assigned = False
#             for robot_idx, available in robot_status.items():
#                 if available and robot_idx in qualified_robot[task]:
#                     thread = threading.Thread(target=execute_task, args=(task, robot_idx))
#                     threads.append(thread)
#                     thread.start()
#                     assigned = True
#                     break
#             if not assigned:
#                 independent_queue.append(task)  # Re-enqueue if no robot available
#
#         # Synchronize all threads
#         for thread in threads:
#             thread.join()
#
#         # Update dependencies for dependent tasks
#         for task in task_batch:
#             for neighbor in graph[task]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     ready_queue.append(neighbor)
#
#
# # Build the task graph and calculate in-degrees
# graph, in_degree = build_graph(dependencies)
#
# # Separate dependent and independent tasks
# dependent_tasks = set(graph.keys()).union(*graph.values())
# independent_tasks = set(subtasks) - dependent_tasks
#
# # Assign tasks dynamically
# print("\nExecuting Tasks:")
# assign_tasks_dynamically(graph, in_degree, independent_tasks, qualified_robot)


### V4
# def build_graph(dependencies):
#     """Build task dependency graph and calculate in-degrees."""
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for src, dst in dependencies:
#         graph[src].append(dst)
#         in_degree[dst] += 1
#
#     for task in subtasks:
#         if task not in in_degree:
#             in_degree[task] = 0  # Tasks with no incoming edges
#
#     return graph, in_degree
#
#
# def separate_dependent_and_independent_tasks(graph, in_degree):
#     """Separate dependent and independent tasks."""
#     dependent_tasks = set(graph.keys()).union(*graph.values())
#     independent_tasks = set(subtasks) - dependent_tasks
#     return list(dependent_tasks), list(independent_tasks)
#
#
# def allocate_tasks(tasks, graph, in_degree, qualified_robot):
#     """Allocate tasks to robots ensuring parallel execution."""
#     assignment = {}  # Task -> Assigned robot
#     available_robots = set(range(len(robots)))  # Set of available robot indices
#     ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])
#
#     while ready_queue:
#         task_batch = list(ready_queue)[:len(available_robots)]  # Limit batch size
#         ready_queue = deque(list(ready_queue)[len(task_batch):])  # Trim ready_queue
#
#         robot_used = set()
#         for task in task_batch:
#             for robot in qualified_robot[task]:
#                 if robot in available_robots and robot not in robot_used:
#                     assignment[task] = robot
#                     robot_used.add(robot)
#                     break
#             else:
#                 # If no robot could be assigned, re-enqueue the task
#                 ready_queue.append(task)
#
#         # Update dependencies and find new ready tasks
#         for task in task_batch:
#             for neighbor in graph[task]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     ready_queue.append(neighbor)
#
#     return assignment
#
#
# def run_tasks(assignment, graph, independent_tasks):
#     """Run tasks either in parallel or sequentially based on dependency levels."""
#     in_degree = {task: 0 for task in subtasks}
#     for src, dsts in graph.items():
#         for dst in dsts:
#             in_degree[dst] += 1
#
#     ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])
#     independent_queue = deque(independent_tasks)
#
#     def execute_task(task, robot_idx):
#         print(f"Task {task} is being executed by robot{robot_idx}")
#         globals()[task](robots[robot_idx])
#         # print(f"Task '{task}' is being executed by {robot_idx}")
#         # time.sleep(1)  # Simulate task duration
#         # print(f"Task '{task}' completed by {robot_idx}")
#
#     while ready_queue or independent_queue:
#         # Process dependent tasks first
#         task_batch = list(ready_queue)[:len(robots)]  # Limit batch size to number of robots
#         ready_queue = deque(list(ready_queue)[len(task_batch):])  # Remove processed tasks
#
#         threads = []
#         for task in task_batch:
#             robot_idx = assignment[task]
#             task_thread = threading.Thread(target=execute_task, args=(task, robot_idx))
#             threads.append(task_thread)
#
#         # Start all threads for dependent tasks
#         for thread in threads:
#             thread.start()
#
#         # Wait for dependent tasks to finish
#         for thread in threads:
#             thread.join()
#
#         # Update dependencies for dependent tasks
#         for task in task_batch:
#             for neighbor in graph[task]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     ready_queue.append(neighbor)
#
#         # Process independent tasks dynamically
#         independent_batch = list(independent_queue)[:len(robots) - len(task_batch)]  # Use remaining robots
#         independent_queue = deque(list(independent_queue)[len(independent_batch):])
#
#         threads = []
#         for task in independent_batch:
#             for robot_idx in qualified_robot[task]:
#                 task_thread = threading.Thread(target=execute_task, args=(task, robot_idx))
#                 threads.append(task_thread)
#                 break
#
#         # Start all threads for independent tasks
#         for thread in threads:
#             thread.start()
#
#         # Wait for independent tasks to finish
#         for thread in threads:
#             thread.join()
#
#
# # Build the task graph and calculate in-degrees
# graph, in_degree = build_graph(dependencies)
#
# # Separate dependent and independent tasks
# dependent_tasks, independent_tasks = separate_dependent_and_independent_tasks(graph, in_degree)
#
# # Allocate tasks to robots
# try:
#     assignment = allocate_tasks(dependent_tasks, graph, in_degree, qualified_robot)
#     print("Task Allocation:")
#     for task, robot_idx in assignment.items():
#         print(f"Task {task} -> robot{robot_idx}")
#
#     # Execute tasks
#     print("\nExecuting Tasks:")
#     run_tasks(assignment, graph, independent_tasks)
#
# except ValueError as e:
#     print(e)


### V3
# def build_graph(dependencies):
#     """Build task dependency graph and calculate in-degrees."""
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for src, dst in dependencies:
#         graph[src].append(dst)
#         in_degree[dst] += 1
#
#     for task in subtasks:
#         if task not in in_degree:
#             in_degree[task] = 0  # Tasks with no incoming edges
#
#     return graph, in_degree
#
#
# def allocate_tasks(subtasks, graph, in_degree, qualified_robot):
#     """Allocate tasks to robots ensuring parallel execution."""
#     assignment = {}  # Task -> Assigned robot
#     available_robots = set(range(len(robots)))  # Set of available robot indices
#     ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])
#
#     while ready_queue:
#         task_batch = list(ready_queue)  # Tasks that can be executed concurrently
#         ready_queue.clear()
#
#         # Assign robots to tasks in the current batch
#         robot_used = set()
#         for task in task_batch:
#             for robot in qualified_robot[task]:
#                 if robot in available_robots and robot not in robot_used:
#                     assignment[task] = robot
#                     robot_used.add(robot)
#                     break
#
#         # Verify all tasks in the batch are assigned
#         if len(task_batch) != len(robot_used):
#             raise ValueError("Not enough robots to execute the current batch of tasks.")
#
#         # Update dependencies and find new ready tasks
#         for task in task_batch:
#             for neighbor in graph[task]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     ready_queue.append(neighbor)
#
#     return assignment
#
#
# def run_tasks(assignment, graph):
#     """Run tasks either in parallel or sequentially based on dependency levels."""
#     in_degree = {task: 0 for task in subtasks}
#     for src, dsts in graph.items():
#         for dst in dsts:
#             in_degree[dst] += 1
#
#     ready_queue = deque([task for task, degree in in_degree.items() if degree == 0])
#
#     def execute_task(task, robot_idx):
#         print(f"Task {task} is being executed by {robots[robot_idx]}")
#         globals()[task](robots[robot_idx])
#         # time.sleep(1)  # Simulate task duration
#         # print(f"Task {task} completed by {robots[robot_idx]}")
#
#     while ready_queue:
#         task_batch = list(ready_queue)  # Tasks at the current level (no dependencies)
#         ready_queue.clear()
#         print(task_batch)
#
#         threads = []  # Store threads for parallel execution
#         for task in task_batch:
#             robot_idx = assignment[task]
#             task_thread = threading.Thread(target=execute_task, args=(task, robot_idx))
#             # print("TASK: ", task, " ROBOT: ", robots[robot_idx])
#             # task_thread = threading.Thread(target=globals()[task], args=(globals()[task], robots[robot_idx]))
#             # print(task_thread)
#             threads.append(task_thread)
#
#         # Start all threads (parallel execution for current level)
#         for thread in threads:
#             thread.start()
#
#         # Wait for all threads to finish
#         for thread in threads:
#             thread.join()
#
#         # Update dependencies and find new ready tasks
#         for task in task_batch:
#             for neighbor in graph[task]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     ready_queue.append(neighbor)
#
#
# # Build the task graph and calculate in-degrees
# graph, in_degree = build_graph(dependencies)
#
# # Allocate tasks to robots
# try:
#     assignment = allocate_tasks(subtasks, graph, in_degree, qualified_robot)
#     print("Task Allocation:")
#     for task, robot_idx in assignment.items():
#         # print(f"Task {task} -> {robots[robot_idx]}")
#         print(f"Task {task} -> {robot_idx}")
#
#     # Execute tasks
#     print("\nExecuting Tasks:")
#     run_tasks(assignment, graph)
#
# except ValueError as e:
#     print(e)



### V2
# # Allocate tasks to robots (preprocessing step)
# def allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots):
#     # Build graph and perform topological sort as in previous implementation
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0
#
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     topo_order = []
#
#     while queue:
#         current = queue.popleft()
#         topo_order.append(current)
#         for neighbor in graph[current]:
#             in_degree[neighbor] -= 1
#             if in_degree[neighbor] == 0:
#                 queue.append(neighbor)
#
#     task_allocation = {}
#
#     def can_assign(robot, task):
#         stack = [task]
#         visited = set()
#         while stack:
#             current = stack.pop()
#             if current in visited:
#                 continue
#             visited.add(current)
#             if robot not in qualified_robot[current]:
#                 return False
#             stack.extend(graph[current])
#         return True
#
#     def assign_task(task, robots):
#         for robot_index in robots:
#             if can_assign(robot_index, task):
#                 task_allocation[task] = robot_index
#                 return True
#         return False
#
#     for task in topo_order:
#         if not assign_task(task, qualified_robot[task]):
#             raise ValueError(f"Task {task} could not be assigned to any robot.")
#
#     robot_task_map = defaultdict(list)
#     for task, robot_index in task_allocation.items():
#         robot_task_map[robots[robot_index]].append(task)
#
#     return robot_task_map
#
#
# robot_task_map = allocate_tasks_with_dependencies(subtasks, dependencies, qualified_robot, robots)
#
# # Execute tasks with dynamic robot availability
# execute_tasks_with_robot_availability(subtasks, dependencies, robot_task_map)


### V1
# # Step 1: Allocate tasks to robots
# def allocate_tasks_with_dependencies(tasks, dependencies, qualified_robot, robots):
#     # Build graph and perform topological sort as in previous implementation
#     graph = defaultdict(list)
#     in_degree = defaultdict(int)
#
#     for pre, nxt in dependencies:
#         graph[pre].append(nxt)
#         in_degree[nxt] += 1
#         if pre not in in_degree:
#             in_degree[pre] = 0
#
#     queue = deque([task for task in in_degree if in_degree[task] == 0])
#     topo_order = []
#
#     while queue:
#         current = queue.popleft()
#         topo_order.append(current)
#         for neighbor in graph[current]:
#             in_degree[neighbor] -= 1
#             if in_degree[neighbor] == 0:
#                 queue.append(neighbor)
#
#     task_allocation = {}
#
#     def can_assign(robot, task):
#         stack = [task]
#         visited = set()
#         while stack:
#             current = stack.pop()
#             if current in visited:
#                 continue
#             visited.add(current)
#             if robot not in qualified_robot[current]:
#                 return False
#             stack.extend(graph[current])
#         return True
#
#     def assign_task(task, robots):
#         for robot_index in robots:
#             if can_assign(robot_index, task):
#                 task_allocation[task] = robot_index
#                 return True
#         return False
#
#     for task in topo_order:
#         if not assign_task(task, qualified_robot[task]):
#             raise ValueError(f"Task {task} could not be assigned to any robot.")
#
#     robot_task_map = defaultdict(list)
#     for task, robot_index in task_allocation.items():
#         # robot_task_map[robots[robot_index]].append(task)
#         robot_task_map[robot_index].append(task)
#
#     return robot_task_map
#
#
# robot_task_map = allocate_tasks_with_dependencies(subtasks, dependencies, qualified_robot, robots)
#
# # Step 2: Execute tasks in parallel
# execute_tasks_in_parallel(subtasks, dependencies, robot_task_map)


### MANUAL EXECUTION
# task_1 = threading.Thread(target=turn_off_lights, args=(robots[0],))
# task_2 = threading.Thread(target=turn_off_floor_lamp, args=(robots[1],))
#
# task_1.start()
# task_2.start()
# task_1.join()
# task_2.join()
#
# put_pen_to_drawer(robots[0])

action_queue.append({'action': 'Done'})
action_queue.append({'action': 'Done'})
action_queue.append({'action': 'Done'})

task_over = True
time.sleep(5)