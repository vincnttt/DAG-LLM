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
                'PickupObject', 'PutObject', 'DropHandObject', 'ThrowObject', 'PushObject', 'PullObject'], 'mass': 100}
]

floor_no = 6

# Start run logs
curr_path = os.path.dirname(__file__)
with open(f"{curr_path}/log.txt", 'a') as f:
    f.write(f"\n\n\n")
    f.write(f"=========== LOGS ===========")

total_exec = 0
success_exec = 0

c = Controller(height=720, width=720)
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
        objs = list([obj["objectId"].rsplit('|', 1)[-1] for obj in c.last_event.metadata["objects"]])
        objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]["objectId"].rsplit('|', 1)[-1]])

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

        action_queue.append({'action': 'PickupSlicedObject', 'objectId': pick_obj_id, 'agent_id': agent_id})
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
    print("Putting: ", put_obj)
    write_log("[Putting]", put_obj)

    robot_name = robot['name']
    agent_id = int(robot_name[-1]) - 1
    objs_sliced = list(set([obj["objectId"].rsplit('|', 1)[-1] for obj in c.last_event.metadata["objects"]]))
    objs_target = list(set([obj["objectId"] for obj in c.last_event.metadata["objects"]]))
    objs_center = list([obj["axisAlignedBoundingBox"]["center"] for obj in c.last_event.metadata["objects"]])
    objs_dists = list([obj["distance"] for obj in c.last_event.metadata["objects"]])

    metadata = c.last_event.events[agent_id].metadata
    robot_location = [metadata["agent"]["position"]["x"], metadata["agent"]["position"]["y"],
                      metadata["agent"]["position"]["z"]]
    dist_to_recp = 9999999  # distance b/w robot and the recp obj
    for idx, (obj_s, obj_t) in enumerate(zip(objs_sliced, objs_target)):
        match = re.match(recp, obj_t)
        if match is not None:
            dist = objs_dists[idx]
            if dist < dist_to_recp:
                recp_obj_id = obj_t
                dest_obj_center = objs_center[idx]
                dist_to_recp = dist

    global recp_id
    # if recp_id is not None:
    #     recp_obj_id = recp_id
    # GoToObject(robot, recp_obj_id)
    # time.sleep(1)
    print("Putting In: ", recp_obj_id, dest_obj_center)
    write_log("[Putting In]", f"{recp_obj_id} {dest_obj_center}")

    action_queue.append({'action': 'PutSlicedObject', 'objectId': recp_obj_id, 'agent_id': agent_id})
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

### TEST CASES 1

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

    PickupSlicedObject(robots, 'BreadSliced_1')

    print(c.last_event.metadata['objects'])

    PutSlicedObject(robots, 'BreadSliced_1', 'Toaster')
    SwitchOn(robots, 'Toaster')
    time.sleep(5)
    SwitchOff(robots, 'Toaster')
    PickupSlicedObject(robots, 'BreadSliced_1')
    GoToObject(robots, 'Plate')
    PutSlicedObject(robots, 'BreadSliced_1', 'Plate')

    print(c.last_event.metadata['objects'])

# def toast_bread(robots):
#     # 0: Subtask 2: Toast the sliced bread.
#     # 1: Go to the sliced bread.
#     GoToObject(robots, 'BreadSliced')
#     # 2: Pick up the sliced bread.
#     PickupObject(robots, 'BreadSliced')
#     # 3: Go to the toaster.
#     GoToObject(robots, 'Toaster')
#     # 4: Put sliced bread in to the toaster.
#     PutObject(robots, 'BreadSliced', 'Toaster')
#     # 5: Switch on the toaster.
#     SwitchOn(robots, 'Toaster')
#     # 6: Wait for a while to let the sliced bread cooked.
#     time.sleep(5)
#     # 7: Switch off the toaster.
#     SwitchOff(robots, 'Toaster')
#
# def serve_toast_on_plate(robots):
#     # 0: Subtask 3: Serve the toast on a plate.
#     # 1: Go to the toaster.
#     GoToObject(robots, 'Toaster')
#     # 2: Pick up the toast.
#     PickupObject(robots, 'BreadSliced')
#     # 3: Go to the plate.
#     GoToObject(robots, 'Plate')
#     # 4: Put the toast on a plate
#     PutObject(robots, 'BreadSliced', 'Plate')

task1_thread = threading.Thread(target=slice_bread, args=(robots[0],))
task1_thread.start()
task1_thread.join()

action_queue.append({'action': 'Done'})
action_queue.append({'action': 'Done'})
action_queue.append({'action': 'Done'})

task_over = True
time.sleep(5)