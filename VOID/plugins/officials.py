import json
from Sibyl_System import INSPECTORS, ENFORCERS, ELEVATED_USERS_FILE

with open(ELEVATED_USERS_FILE, "r") as f:
    data = json.load(f)

async def add_inspector(user_id) -> bool:
    user_id = int(user_id)
    if user_id in INSPECTORS:
        return False
    if user_id in data["ENFORCERS"]:
        data["ENFORCERS"].remove(user_id)
    data["INSPECTORS"].append(user_id)
    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)
    return True

async def rem_inspector(user_id) -> bool:
    user_id = int(user_id)
    data["INSPECTORS"].remove(user_id)
    data["ENFORCERS"].append(user_id)
    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)
    return True

async def add_enforcers(user_id) -> bool:
    user_id = int(user_id)
    if user_id in ENFORCERS:
        return False
    data["ENFORCERS"].append(user_id)
    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)
    return True

async def rem_enforcers(user_id) -> bool:
    user_id = int(user_id)
    data["ENFORCERS"].remove(user_id)
    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)
    return True

