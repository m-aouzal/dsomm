# file: app/blueprints/conflict_resolution.py

from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os

conflict_resolution = Blueprint("conflict_resolution", __name__)

DATA_FOLDER = "./data"
USER_RESPONSES_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
LEVEL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "level_activities.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")
PIPELINE_ORDER_FILE   = os.path.join(DATA_FOLDER, "pipeline_order.json")

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

@conflict_resolution.route("/", methods=["GET", "POST"])
def resolve_conflict():
    """
    1) Gathers user-chosen level, stages, tools from session.
    2) Builds an 'activities' list covering levels 1..selected_level.
    3) Applies user-chosen tools (incl. custom) to mark coverage or conflicts.
    4) Renders a template letting the user pick multiple or "none" for each activity.
    5) Saves final coverage in user_responses.json.
    """
    # 1. Gather data from session
    chosen_level  = session.get("security_level", "1")
    chosen_stages = session.get("stages", [])
    stage_tools   = session.get("tools", {})  # {stage: {"standard": [...], "custom": [...]} }

    # If user didn't pick level/stages, redirect to some earlier step
    if not chosen_stages or not chosen_level:
        return redirect(url_for("stages.select_stages"))

    # 2. Build an 'activities' list from level_activities.json for levels 1..chosen_level
    level_acts_data = load_json(LEVEL_ACTIVITIES_FILE)  # e.g. { "1":[{Activity:"A1"},...], "2":[...], etc. }
    activities = _build_activities_for_levels(chosen_level, level_acts_data)

    # 3. Merge user-chosen tools into 'activities', marking coverage/conflicts
    tool_acts_data = load_json(TOOL_ACTIVITIES_FILE)    # e.g. { "GitLab CI/CD": ["Act1","Act2"], ... }
    _apply_tools_to_activities(activities, chosen_stages, stage_tools, tool_acts_data)

    # 4. If POST => user resolves final coverage by picking multiple or "none"
    if request.method == "POST":
        for idx, act_item in enumerate(activities):
            chosen_list = request.form.getlist(f"choice_{idx}")
            if "none" in chosen_list:
                act_item["status"] = "unimplemented"
                act_item["tools"]  = {}
                act_item["custom"] = []
            else:
                if not chosen_list:
                    # no picks => unimplemented
                    act_item["status"] = "unimplemented"
                    act_item["tools"]  = {}
                    act_item["custom"] = []
                else:
                    act_item["status"] = "implemented"
                    # keep only chosen
                    for t_name in list(act_item["tools"].keys()):
                        if t_name in chosen_list:
                            act_item["tools"][t_name] = "checked"
                        else:
                            del act_item["tools"][t_name]
                    # remove unpicked custom
                    for ctool in list(act_item["custom"]):
                        if ctool not in chosen_list:
                            act_item["custom"].remove(ctool)

        # 5. Save final coverage
        user_responses = {
            "selected_level": chosen_level,
            "stages": chosen_stages,
            "tools": stage_tools,
            "activities": activities
        }
        save_json(USER_RESPONSES_FILE, user_responses)

        # Possibly redirect to next step or re-check conflict
        return redirect(url_for("conflict_resolution.resolve_conflict"))

    # If GET => show conflict_resolution.html
    return render_template("conflict_resolution.html", activities=activities)

# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def _build_activities_for_levels(chosen_level_str, level_acts_data):
    """
    Builds a list of activity dicts for levels 1..N (N=chosen_level_str).
    structure: { "activity":..., "description":..., "status":"unimplemented", "custom":[], "tools":{} }
    """
    try:
        max_lvl = int(chosen_level_str)
    except ValueError:
        max_lvl = 1

    results = []
    for lvl in range(1, max_lvl+1):
        # lvl_acts_data might have str keys like "1","2","3"
        for act_obj in level_acts_data.get(str(lvl), []):
            results.append({
                "activity": act_obj["Activity"],
                "description": act_obj.get("Description",""),
                "status": "unimplemented",
                "custom": [],
                "tools": {}
            })
    return results

def _apply_tools_to_activities(activities, chosen_stages, stage_tools, tool_acts_data):
    """
    For each stage, gather standard+custom tools => see which activities each tool covers.
    If multiple tools claim same activity => conflict => mark them "temporary".
    If single => "checked".
    If custom tool => also mark it in activity["custom"].
    """
    # Build a quick map activityName->reference to item in activities
    act_map = {item["activity"]: item for item in activities}

    for stage in chosen_stages:
        st_data = stage_tools.get(stage, {"standard": [], "custom": []})
        all_tools = list(st_data["standard"]) + list(st_data["custom"])

        for tool_name in all_tools:
            if tool_name == "none":
                continue
            covered = tool_acts_data.get(tool_name, [])
            for act_name in covered:
                if act_name not in act_map:
                    continue
                act_item = act_map[act_name]
                if not act_item["tools"]:
                    # first tool => "checked"
                    act_item["tools"][tool_name] = "checked"
                    act_item["status"] = "implemented"
                else:
                    # conflict => set existing & new to "temporary"
                    if tool_name not in act_item["tools"]:
                        act_item["tools"][tool_name] = "temporary"
                    for t, val in act_item["tools"].items():
                        if val == "checked":
                            act_item["tools"][t] = "temporary"
                    act_item["status"] = "temporary"

                if tool_name in st_data["custom"] and tool_name not in act_item["custom"]:
                    act_item["custom"].append(tool_name)
