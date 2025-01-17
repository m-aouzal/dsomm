from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os

###############################################################################
# Blueprint and Config
###############################################################################

conflict_resolution = Blueprint("conflict_resolution", __name__)

DATA_FOLDER = "./data"  # You might want to make this configurable
USER_RESPONSES_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
LEVEL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "level_activities.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")
PIPELINE_ORDER_FILE = os.path.join(DATA_FOLDER, "pipeline_order.json")
STAGE_DEFAULTS_FILE = os.path.join(DATA_FOLDER, "stage_defaults.json")

###############################################################################
# Utility Functions for Loading and Saving JSON
###############################################################################

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[DEBUG] File not found: {path}. Returning an empty dict.")
        return {}

def save_json(path, data):
    print(f"[DEBUG] Saving data to {path}:\n", json.dumps(data, indent=2, ensure_ascii=False))
    with open(path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

###############################################################################
# Helper Functions
###############################################################################

def load_configuration_data():
    """Loads data from all JSON configuration files."""
    return {
        "level_activities": load_json(LEVEL_ACTIVITIES_FILE),
        "tool_activities": load_json(TOOL_ACTIVITIES_FILE),
        "pipeline_order": load_json(PIPELINE_ORDER_FILE),
        "stage_defaults": load_json(STAGE_DEFAULTS_FILE),
    }

def get_activities_for_level(level, level_activities_data):
    """Returns a list of activities for the selected security level."""
    try:
        max_lvl = int(level)
    except ValueError:
        max_lvl = 1

    activities = []
    for lvl in range(1, max_lvl + 1):
        level_key = str(lvl)
        lvl_activities = level_activities_data.get(level_key, [])
        print(f"[DEBUG] Level={lvl}, activities found: {len(lvl_activities)}")
        for act_obj in lvl_activities:
            activities.append({
                "activity": act_obj.get("Activity", f"Activity-L{lvl}"),
                "description": act_obj.get("Description", ""),
                "status": "unimplemented",
                "custom": [],
                "tools": {}
            })
    return activities

def initialize_activity_statuses(activities):
    """Initializes the status of each activity."""
    # This function is likely not needed as it's done in get_activities_for_level
    return activities

def apply_standard_tool_selection(activity_status, stage, tool_name, tool_activities_data):
    """Applies standard tool selection to activities, handling conflicts."""
    print(f"[DEBUG] Applying standard tool selection for stage: {stage}, tool: {tool_name}")
    
    if tool_name == "none":
        return
    
    tool_data = tool_activities_data.get(tool_name, {})
    if not tool_data:
        print(f"[DEBUG] Tool '{tool_name}' not found in tool_activities.json")
        return

    for activity in tool_data.get("Activities", []):
        act_name = activity.get("Activity")
        if act_name not in activity_status:
            continue

        act_item = activity_status[act_name]

        if not act_item["tools"]:
            act_item["tools"][tool_name] = "checked"
            act_item["status"] = "checked" if act_item["status"] == "unimplemented" else act_item["status"]
        elif tool_name not in act_item["tools"]:
            act_item["tools"][tool_name] = "temporary"
            for existing_tool in act_item["tools"]:
                if act_item["tools"][existing_tool] == "checked":
                    act_item["tools"][existing_tool] = "temporary"
            act_item["status"] = "temporary"

def apply_custom_tool_selection(activity_status, stage, tool_name, stage_defaults):
    """Applies custom tool selection to activities based on stage defaults."""
    print(f"[DEBUG] Applying custom tool selection for stage: {stage}, tool: {tool_name}")

    stage_data = stage_defaults.get(stage, {}).get("activities", [])
    if not stage_data:
        print(f"[DEBUG] No activities found for stage '{stage}' in stage_defaults.json")
        return

    for act_name in stage_data:
        if act_name not in activity_status:
            continue

        act_item = activity_status[act_name]

        # Add the custom tool to the activity's custom array
        if "custom" not in act_item:
            act_item["custom"] = []
        if tool_name not in act_item["custom"]:
            act_item["custom"].append(tool_name)

        # Update activity status based on stage defaults and existing status
        if act_item["status"] == "unimplemented":
            act_item["status"] = "checked"
        elif act_item["status"] in ["checked", "implemented"]:
            act_item["status"] = "temporary"

        # If the activity status is now 'checked', ensure the custom tool is marked as such in 'tools'
        if act_item["status"] == "checked":
            act_item["tools"][tool_name] = "checked"

def recalculate_activity_statuses(activity_status):
    """Re-evaluates all activity statuses after each user selection or conflict resolution."""
    for act_name, act_item in activity_status.items():
        if act_item["status"] == "unimplemented":
            continue  # No need to recalculate

        # Check if all tools are in agreement ("checked")
        tools_statuses = act_item["tools"].values()
        all_tools_checked = all(status == "checked" for status in tools_statuses)
        
        if all_tools_checked and not act_item["custom"]:
            act_item["status"] = "implemented"
        elif len(act_item["tools"]) > 1 or (act_item["custom"] and act_item["tools"]):
            # Set to temporary if we have multiple tools in agreement or a custom tool is present with other tools
            act_item["status"] = "temporary"
        elif len(act_item["tools"]) == 1 and "checked" in act_item["tools"].values() and not act_item["custom"]:
             act_item["status"] = "implemented"
        elif len(act_item["tools"]) == 1 and "checked" in act_item["tools"].values():
            act_item["status"] = "temporary"

def resolve_conflicts(activity_status, form_data):
    """Handles the interactive conflict resolution process."""
    print("[DEBUG] Resolving conflicts...")
    
    for act_name, act_item in activity_status.items():
        if act_item["status"] == "temporary":
            chosen_list = form_data.getlist(f"choice_{act_name}")
            new_custom_tool = form_data.get(f"new_custom_{act_name}", "").strip()

            print(f"[DEBUG] Activity: {act_name}, Chosen list: {chosen_list}, New custom tool: {new_custom_tool}")

            if "none" in chosen_list:
                act_item["status"] = "unimplemented"
                act_item["tools"] = {}
                act_item["custom"] = []
            else:
                act_item["status"] = "implemented"

                # Handle standard tools
                for t_name in list(act_item["tools"].keys()):
                    if t_name in chosen_list:
                        act_item["tools"][t_name] = "checked"
                    else:
                        del act_item["tools"][t_name]

                # Handle existing custom tools
                for i in range(len(act_item["custom"]) - 1, -1, -1):
                    c_tool = act_item["custom"][i]
                    if c_tool not in chosen_list:
                        act_item["custom"].pop(i)

                # Add new custom tool
                if new_custom_tool:
                    if "custom" not in act_item:
                        act_item["custom"] = []
                    if new_custom_tool not in act_item["custom"]:
                        act_item["custom"].append(new_custom_tool)
                    act_item["tools"][new_custom_tool] = "checked"

                

def perform_gap_analysis(activity_status):
    """Identifies gaps ("unimplemented" activities) and guides the user through addressing them."""
    # Implementation for gap analysis will go here
    pass

def generate_summary_report(activity_status, user_selections):
    """Creates the final summary report."""
    # Implementation for generating the summary report will go here
    pass

def _debug_temporary_activities(activities):
    """
    Affiche des messages de debug spécifiques pour 
    toutes les activités ayant status='temporary'.
    Montre également quels outils (tools) sont en 'temporary' ou 'checked'.
    """
    print("[DEBUG] Vérification des activités en 'temporary' :")
    temporary_acts = [a for a in activities if a.get("status") == "temporary"]
    if not temporary_acts:
        print("    Aucune activité 'temporary' détectée.")
        return

    for act in temporary_acts:
        print(f"    [DEBUG] Activité TEMPORAIRE: {act['activity']}")
        print(f"           - Description: {act.get('description', 'N/A')}")
        print(f"           - Custom Tools: {act['custom']}")
        if act["tools"]:
            print(f"           - Outils dans 'tools':")
            for t_name, t_status in act["tools"].items():
                print(f"               * {t_name} : {t_status}")
        else:
            print("           - Aucune entrée dans 'tools'.")

###############################################################################
# Main Route: Conflict Resolution
###############################################################################

@conflict_resolution.route("/", methods=["GET", "POST"])
def resolve_conflict():
    """
    Main process for conflict detection and resolution.
    """
    config_data = load_configuration_data()
    level_activities_data = config_data["level_activities"]
    tool_activities_data = config_data["tool_activities"]
    pipeline_order_data = config_data["pipeline_order"]
    stage_defaults_data = config_data["stage_defaults"]

    chosen_level = session.get("security_level", "1")
    chosen_stages = session.get("stages", [])
    stage_tools = session.get("tools", {})

    print("[DEBUG] Lancement du resolve_conflict.")
    print("[DEBUG] Niveau choisi :", chosen_level)
    print("[DEBUG] Étapes choisies :", chosen_stages)
    print("[DEBUG] Outils choisis (par étape) :", json.dumps(stage_tools, indent=2, ensure_ascii=False))

    if not chosen_stages or not chosen_level:
        print("[DEBUG] Pas de level ou de stages dans la session. Redirection vers stages.")
        return redirect(url_for("stages.select_stages"))

    activities = get_activities_for_level(chosen_level, level_activities_data)
    activities_map = {activity["activity"]: activity for activity in activities}

    for stage in chosen_stages:
        stage_data = stage_tools.get(stage, {"standard": [], "custom": []})
        for tool in stage_data["standard"]:
            apply_standard_tool_selection(activities_map, stage, tool, tool_activities_data)
        for tool in stage_data["custom"]:
            apply_custom_tool_selection(activities_map, stage, tool, stage_defaults_data)

    recalculate_activity_statuses(activities_map)

    # Debug: Show temporary activities after initial tool application
    _debug_temporary_activities(list(activities_map.values()))

    if request.method == "POST":
        print("[DEBUG] Form POST reçu:", dict(request.form))
        resolve_conflicts(activities_map, request.form)
        recalculate_activity_statuses(activities_map)

        user_responses = {
            "selected_level": chosen_level,
            "stages": chosen_stages,
            "tools": stage_tools,
            "activities": list(activities_map.values())
        }
        save_json(USER_RESPONSES_FILE, user_responses)

        # Check if there are still unresolved conflicts
        unresolved_conflicts = any(act["status"] == "temporary" for act in activities_map.values())
        if unresolved_conflicts:
            # We still have unresolved conflicts, so refresh the conflict resolution page
            print("[DEBUG] Il reste des conflits non résolus. Rechargement de la page.")
            return redirect(url_for("conflict_resolution.resolve_conflict"))
        else:
            print("[DEBUG] Tous les conflits sont résolus. Redirection vers le résumé final.")
            return redirect(url_for("summary.display_summary"))

    # For GET requests, we display the conflict resolution form
    # Only display activities that are in 'temporary' status
    activities_to_display = [act for act in activities_map.values() if act["status"] == "temporary"]

    return render_template("conflict_resolution.html", activities=activities_to_display)