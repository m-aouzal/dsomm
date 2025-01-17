from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os

###############################################################################
# Blueprint and Config
###############################################################################
conflict_resolution = Blueprint("conflict_resolution", __name__)

DATA_FOLDER = "./data"
USER_RESPONSES_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
LEVEL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "level_activities.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")
PIPELINE_ORDER_FILE = os.path.join(DATA_FOLDER, "pipeline_order.json")
STAGE_DEFAULTS_FILE = os.path.join(DATA_FOLDER, "stage_defaults.json")

###############################################################################
# Utility
###############################################################################
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[DEBUG] File not found: {path}. Returning empty dict.")
        return {}

def save_json(path, data):
    print(f"[DEBUG] Saving data to {path}:\n", json.dumps(data, indent=2, ensure_ascii=False))
    with open(path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

###############################################################################
# Debug: Show temporary activities
###############################################################################
def _debug_temporary_activities(activities):
    print("[DEBUG] Vérification des activités en 'temporary' :")
    temp_list = [a for a in activities if a.get("status") == "temporary"]
    if not temp_list:
        print("    Aucune activité 'temporary' détectée.")
        return
    for act in temp_list:
        print(f"    [DEBUG] Activité TEMPORAIRE: {act['activity']}")
        print(f"           - Description: {act.get('description', 'N/A')}")
        print(f"           - Custom Tools: {act['custom']}")
        if act["tools"]:
            print("           - Outils dans 'tools':")
            for t_name in act["tools"]:
                print(f"               * {t_name}")
        else:
            print("           - Aucune entrée dans 'tools'.")

###############################################################################
# Loading the Various Configs
###############################################################################
def load_configuration_data():
    return {
        "level_activities": load_json(LEVEL_ACTIVITIES_FILE),
        "tool_activities": load_json(TOOL_ACTIVITIES_FILE),
        "pipeline_order": load_json(PIPELINE_ORDER_FILE),
        "stage_defaults": load_json(STAGE_DEFAULTS_FILE),
    }

def get_activities_for_level(level, level_activities_data):
    try:
        max_lvl = int(level)
    except ValueError:
        max_lvl = 1

    all_acts = []
    for lv in range(1, max_lvl + 1):
        level_key = str(lv)
        lvl_list = level_activities_data.get(level_key, [])
        print(f"[DEBUG] Level={lv}, activities found: {len(lvl_list)}")
        for act_obj in lvl_list:
            all_acts.append({
                "activity": act_obj.get("Activity", f"Activity-L{lv}"),
                "description": act_obj.get("Description", ""),
                "status": "unimplemented",
                "custom": [],
                "tools": {}
            })
    return all_acts

###############################################################################
# Tools Application
###############################################################################
def apply_standard_tool_selection(activity_map, stage, tool_name, tool_activities_data):
    if tool_name == "none":
        return
    tool_data = tool_activities_data.get(tool_name, {})
    if not tool_data:
        print(f"[DEBUG] Standard tool '{tool_name}' not found.")
        return
    covered_acts = tool_data.get("Activities", [])
    for it in covered_acts:
        act_name = it.get("Activity")
        if act_name not in activity_map:
            continue
        act_item = activity_map[act_name]
        if tool_name not in act_item["tools"]:
            act_item["tools"][tool_name] = "checked"
        if act_item["status"] == "unimplemented":
            act_item["status"] = "checked"
        elif act_item["status"] == "checked":
            act_item["status"] = "temporary"

def apply_custom_tool_selection(activity_map, stage, tool_name, stage_defaults):
    stage_info = stage_defaults.get(stage, {}).get("activities", [])
    if not stage_info:
        print(f"[DEBUG] No defaults found for stage: {stage}")
        return
    for act_name in stage_info:
        if act_name not in activity_map:
            continue
        act_item = activity_map[act_name]
        act_item["tools"][tool_name] = "checked"
        if tool_name not in act_item["custom"]:
            act_item["custom"].append(tool_name)
        if act_item["status"] == "unimplemented":
            act_item["status"] = "checked"
        elif act_item["status"] in ["checked", "implemented"]:
            act_item["status"] = "temporary"

def recalc_statuses(activity_map):
    """Re-check each activity's status after modifications."""
    for act_name, act_item in activity_map.items():
        if not act_item["tools"]:
            act_item["status"] = "unimplemented"
            continue
        num_tools = len(act_item["tools"])
        if num_tools > 1:
            act_item["status"] = "temporary"
        elif num_tools == 1:
            act_item["status"] = "checked"

###############################################################################
# Conflict Resolution
###############################################################################
def resolve_conflicts(activity_map, form_data):
    print("[DEBUG] Resolving conflicts from user POST...")

    # Loop over each activity that is 'temporary'
    for act_name, act_item in activity_map.items():
        if act_item["status"] == "temporary":
            chosen_list = form_data.getlist(f"choice_{act_name}")
            new_custom_tool = form_data.get(f"new_custom_{act_name}", "").strip()
            print(f"[DEBUG] Conflict Activity='{act_name}', chosen={chosen_list}, new_custom='{new_custom_tool}'")

            # If user picks 'none', it's unimplemented
            if "none" in chosen_list:
                act_item["status"] = "unimplemented"
                act_item["tools"].clear()
                act_item["custom"].clear()
                continue

            # If the user picks at least one tool => implemented
            if chosen_list:
                act_item["status"] = "implemented"
                # Keep only chosen tools
                updated_tools = {}
                for t_name in chosen_list:
                    if t_name in act_item["tools"]:
                        updated_tools[t_name] = "checked"
                # Overwrite the old dict
                act_item["tools"] = updated_tools
                # Keep only the chosen custom
                act_item["custom"] = [ct for ct in act_item["custom"] if ct in chosen_list]

                # If the user typed a new custom tool, add it
                if new_custom_tool:
                    if new_custom_tool not in act_item["custom"]:
                        act_item["custom"].append(new_custom_tool)
                    act_item["tools"][new_custom_tool] = "checked"

            else:
                # If no checkboxes, user wants it unimplemented
                act_item["status"] = "unimplemented"
                act_item["tools"].clear()
                act_item["custom"].clear()

###############################################################################
# Main Route
###############################################################################
@conflict_resolution.route("/", methods=["GET", "POST"])
def resolve_conflict():
    config = load_configuration_data()
    lvl_acts_data = config["level_activities"]
    tool_acts_data = config["tool_activities"]
    stage_defs = config["stage_defaults"]

    chosen_level = session.get("security_level", "1")
    chosen_stages = session.get("stages", [])
    stage_tools = session.get("tools", {})

    print("[DEBUG] Lancement du resolve_conflict.")
    print("[DEBUG] Niveau choisi :", chosen_level)
    print("[DEBUG] Étapes choisies :", chosen_stages)
    print("[DEBUG] Outils choisis (par étape) :", json.dumps(stage_tools, indent=2, ensure_ascii=False))

    if not chosen_stages or not chosen_level:
        print("[DEBUG] Missing chosen_stages or chosen_level, redirecting.")
        return redirect(url_for("stages.select_stages"))

    # Build the activities
    acts = get_activities_for_level(chosen_level, lvl_acts_data)
    activity_map = {a["activity"]: a for a in acts}

    # Apply the tools to see if anything becomes 'temporary'
    for stage in chosen_stages:
        data_for_stage = stage_tools.get(stage, {"standard": [], "custom": []})
        for std_tool in data_for_stage["standard"]:
            apply_standard_tool_selection(activity_map, stage, std_tool, tool_acts_data)
        for c_tool in data_for_stage["custom"]:
            apply_custom_tool_selection(activity_map, stage, c_tool, stage_defs)

    # Recalculate statuses now
    recalc_statuses(activity_map)

    # If POST => user is finishing conflict resolution
    if request.method == "POST":
        print("[DEBUG] Form POST reçu:", dict(request.form))
        # Attempt to resolve conflicts (temporary activities)
        resolve_conflicts(activity_map, request.form)
        recalc_statuses(activity_map)

        # Save
        user_responses = {
            "selected_level": chosen_level,
            "stages": chosen_stages,
            "tools": stage_tools,
            "activities": list(activity_map.values())
        }
        save_json(USER_RESPONSES_FILE, user_responses)

        # If any remain temporary, reload. Otherwise => summary
        still_temporary = any(a["status"] == "temporary" for a in activity_map.values())
        if still_temporary:
            print("[DEBUG] Des activités demeurent 'temporary'. Rechargement du conflict resolution.")
            return redirect(url_for("conflict_resolution.resolve_conflict"))
        else:
            print("[DEBUG] Plus de conflits => vers summary.")
            return redirect(url_for("summary.display_summary"))

    # GET: show only the 'temporary' activities
    to_display = [a for a in activity_map.values() if a["status"] == "temporary"]
    if not to_display:
        # If there is no conflict => redirect to summary
        print("[DEBUG] Aucune activité 'temporary'. On redirige vers summary directement.")
        return redirect(url_for("summary.display_summary"))

    # Debug
    print("[DEBUG] Checking for temporary conflicts after initial tool application:")
    _debug_temporary_activities(list(activity_map.values()))

    return render_template("conflict_resolution.html", activities=to_display)
