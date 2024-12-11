
def analyze_generated_function():
    file_path = __file__

    with open(file_path, "r") as f:
        source_code = f.read()

    tree = ast.parse(source_code)

    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    # Analyze each function
    results = {}
    for func in functions:
        func_name = func.name  # Get the name of the function
        num_statements = len(func.body)  # Count the number of statements in the function body
        results[func_name] = num_statements

    return results


for i in range(25):
    action_queue.append({'action': 'Done'})
    action_queue.append({'action': 'Done'})
    action_queue.append({'action': 'Done'})
    time.sleep(0.1)

task_over = True
time.sleep(5)

print(f"Success: {success_exec}, Total: {total_exec}")

try:
    exec = float(success_exec) / float(total_exec)
except ZeroDivisionError:
    exec = 0.0

write_log("\n[GROUND TRUTH]", ground_truth)

print(ground_truth)
objs = list([obj for obj in c.last_event.metadata["objects"]])

gcr_tasks = 0.0
gcr_complete = 0.0
for obj_gt in ground_truth:
    obj_name = obj_gt['name']
    state = obj_gt['state']
    contains = obj_gt['contains']
    gcr_tasks += 1
    for obj in objs:
        # if obj_name in obj["name"]:
        #     print (obj)
        if state == 'SLICED':
            if obj_name in obj["name"] and obj["isSliced"]:
                gcr_complete += 1

        if state == 'OFF':
            if obj_name in obj["name"] and not obj["isToggled"]:
                gcr_complete += 1

        if state == 'ON':
            if obj_name in obj["name"] and obj["isToggled"]:
                gcr_complete += 1

        if state == 'HOT':
            # print (obj)
            if obj_name in obj["name"] and obj["temperature"] == 'Hot':
                gcr_complete += 1

        if state == 'COOKED':
            if obj_name in obj["name"] and obj["isCooked"]:
                gcr_complete += 1

        if state == 'OPENED':
            if obj_name in obj["name"] and obj["isOpen"]:
                gcr_complete += 1

        if state == 'CLOSED':
            if obj_name in obj["name"] and not obj["isOpen"]:
                gcr_complete += 1

        if state == 'PICKED':
            if obj_name in obj["name"] and obj["isPickedUp"]:
                gcr_complete += 1

        if len(contains) != 0 and obj_name in obj["name"]:
            print(contains, obj_name, obj["name"])
            write_log("[DATA]", f"{contains}, {obj_name}, {obj['name']}")
            for rec in contains:
                if obj['receptacleObjectIds'] is not None:
                    for r in obj['receptacleObjectIds']:
                        print(rec, r)
                        write_log("[DATA]", f"{rec}, {r}")
                        if rec in r:
                            print(rec, r)
                            write_log("[DATA]", f"{rec}, {r}")
                            gcr_complete += 1

sr = 0
tc = 0
if gcr_tasks == 0:
    gcr = 1
else:
    gcr = gcr_complete / gcr_tasks

if gcr == 1.0:
    tc = 1

max_trans += 1
no_trans_gt += 1
print(no_trans_gt, max_trans, no_trans)

if max_trans == no_trans_gt and no_trans_gt == no_trans:
    ru = 1
elif max_trans == no_trans_gt:
    ru = 0
else:
    ru = (max_trans - no_trans) / (max_trans - no_trans_gt)

if tc == 1 and ru == 1:
    sr = 1

print(f"SR:{sr}, TCR:{tc}, GCR:{gcr}, Exec:{exec}, RU:{ru}")
with open(f"{curr_path}/log.txt", 'a') as f:
    f.write(f"\n\n\n")
    f.write(f"========== RESULT ==========")
    f.write(f"\n\n")
    f.write(f"no_trans_gt: {no_trans_gt}, max_trans: {max_trans}, no_trans: {no_trans}")
    f.write(f"\n")
    f.write(f"SR:{sr}, TCR:{tc}, GCR:{gcr}, RU:{ru}, Exec:{exec}")

generate_video()