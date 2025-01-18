from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
from .utils import (
    prepare_activities_for_gap_analysis,
    get_activities_for_level,
    apply_standard_tool_selection,
    apply_custom_tool_selection
)

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
    """Save data to JSON file with proper encoding and error handling."""
    try:
        print(f"[DEBUG] Attempting to save data to {path}")
        print("[DEBUG] Data structure before saving:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Ensure the activities list is properly formatted
        if "activities" in data:
            print(f"[DEBUG] Number of activities to save: {len(data['activities'])}")
            for act in data["activities"]:
                if "status" not in act:
                    print(f"[WARNING] Activity {act.get('activity', 'unknown')} missing status")
                if "tools" not in act:
                    print(f"[WARNING] Activity {act.get('activity', 'unknown')} missing tools")
        
        # Write to file with proper encoding
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # Verify the save
        with open(path, "r", encoding='utf-8') as f:
            saved_data = json.load(f)
            print(f"[DEBUG] Verified saved data contains {len(saved_data.get('activities', []))} activities")
            
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save data to {path}: {str(e)}")
        return False

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

###############################################################################
# Conflict Resolution
###############################################################################
def resolve_conflicts(activity_map, form_data):
    print("[DEBUG] Resolving conflicts from user POST...")

    for act_name, act_item in activity_map.items():
        if act_item["status"] == "temporary":
            chosen_list = form_data.getlist(f"choice_{act_name}")
            new_custom_tool = form_data.get(f"new_custom_{act_name}", "").strip()
            
            print(f"[DEBUG] Processing conflict for '{act_name}':")
            print(f"  - Chosen tools: {chosen_list}")
            print(f"  - New custom tool: {new_custom_tool}")

            if "none" in chosen_list:
                act_item["status"] = "unimplemented"
                act_item["tools"].clear()
                act_item["custom"].clear()
                print(f"  - Marked as unimplemented")
            elif chosen_list:
                # Keep only selected tools
                new_tools = {}
                for tool_name in chosen_list:
                    new_tools[tool_name] = "checked"
                
                # Add new custom tool if provided
                if new_custom_tool:
                    new_tools[new_custom_tool] = "checked"
                    if new_custom_tool not in act_item["custom"]:
                        act_item["custom"].append(new_custom_tool)

                # Update tools and custom lists
                act_item["tools"] = new_tools
                act_item["custom"] = [t for t in act_item["custom"] 
                                    if t in chosen_list or t == new_custom_tool]
                
                # If user has made a selection, mark as implemented
                act_item["status"] = "implemented"
                
                print(f"  - Final status: {act_item['status']}")
                print(f"  - Final tools: {act_item['tools']}")
                print(f"  - Final custom tools: {act_item['custom']}")
            else:
                act_item["status"] = "unimplemented"
                act_item["tools"].clear()
                act_item["custom"].clear()
                print(f"  - Marked as unimplemented (no tools selected)")

def recalculate_activity_statuses(activity_map):
    """Only recalculate statuses for activities that aren't already resolved."""
    for act_name, act_item in activity_map.items():
        # Skip activities that have been resolved through conflict resolution
        if act_item["status"] in ["implemented", "unimplemented"]:
            continue
            
        # For other activities, calculate based on tools
        if not act_item["tools"]:
            act_item["status"] = "unimplemented"
        elif len(act_item["tools"]) > 1:
            act_item["status"] = "temporary"
        else:
            act_item["status"] = "checked"

###############################################################################
# Main Route
###############################################################################
@conflict_resolution.route("/", methods=["GET", "POST"])
def resolve_conflict():
    # Load existing user responses first
    user_responses = load_json(USER_RESPONSES_FILE)
    
    config = load_configuration_data()
    lvl_acts_data = config["level_activities"]
    tool_acts_data = config["tool_activities"]
    stage_defs = config["stage_defaults"]

    chosen_level = session.get("security_level", "1")
    chosen_stages = session.get("stages", [])
    stage_tools = session.get("tools", {})

    print("[DEBUG] Lancement du resolve_conflict.")
    print("[DEBUG] Current user_responses:", json.dumps(user_responses, indent=2, ensure_ascii=False))

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

    if request.method == "POST":
        print("[DEBUG] Form POST reçu:", dict(request.form))
        resolve_conflicts(activity_map, request.form)
        recalculate_activity_statuses(activity_map)

        user_responses = {
            "selected_level": chosen_level,
            "stages": chosen_stages,
            "tools": stage_tools,
            "activities": list(activity_map.values())
        }
        save_json(USER_RESPONSES_FILE, user_responses)

        # Check for remaining temporary activities
        temporary_activities = [a for a in activity_map.values() if a["status"] == "temporary"]
        if not temporary_activities:
            print("[DEBUG] No more temporary activities, redirecting to gap analysis")
            return redirect(url_for("gap_analysis.analyze_gaps"))
        
        print("[DEBUG] Still have temporary activities, staying on conflict resolution")
        return redirect(url_for("conflict_resolution.resolve_conflict"))

    # GET: show only the 'temporary' activities
    to_display = [a for a in activity_map.values() if a["status"] == "temporary"]
    if not to_display:
        print("[DEBUG] No temporary activities found, redirecting to summary")
        return redirect(url_for("summary.display_summary"))

    _debug_temporary_activities(list(activity_map.values()))
    return render_template("conflict_resolution.html", activities=to_display)
