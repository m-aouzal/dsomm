from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
from .utils import apply_standard_tool_selection

gap_analysis = Blueprint("gap_analysis", __name__)

DATA_FOLDER = "./data"
GAP_FILE = os.path.join(DATA_FOLDER, "gap.json")
USER_RESPONSES_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")
CUSTOM_TOOLS_FILE = os.path.join(DATA_FOLDER, "custom_tools.json")
LEVEL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "level_activities.json")
TOOLS_FILE = os.path.join(DATA_FOLDER, "tools.json")

def load_json(path):
    """Load JSON file with error handling."""
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[DEBUG] File not found: {path}")
        return {}

def save_json(path, data):
    try:
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save data to {path}: {str(e)}")
        return False


def get_relevant_tools(activity, user_responses, tool_activities):
    """Get tools relevant to the current activity."""
    relevant_tools = {
        "standard": [],
        "custom": [],
        "user_selected": []
    }
    
    print(f"[DEBUG] Getting relevant tools for activity: '{activity['activity']}'")
    
    # Get standard tools that can implement this activity
    for tool_name, tool_data in tool_activities.items():
        for tool_activity in tool_data.get("Activities", []):
            if tool_activity.get("Activity") == activity["activity"]:
                print(f"[DEBUG] Found standard tool '{tool_name}' for activity '{activity['activity']}'")
                if tool_name not in relevant_tools["standard"]:
                    relevant_tools["standard"].append(tool_name)
    
    # Get user's previously selected tools
    for stage, stage_data in user_responses.get("tools", {}).items():
        print(f"[DEBUG] Checking user tools for stage: '{stage}'")
        # Add standard tools from user responses
        for tool in stage_data.get("standard", []):
            if tool != "none":
                if tool in relevant_tools["standard"]:
                    print(f"[DEBUG] Adding user-selected standard tool '{tool}' from stage '{stage}'")
                    if tool not in relevant_tools["user_selected"]:
                        relevant_tools["user_selected"].append(tool)
                else:
                    print(f"[DEBUG] Standard tool '{tool}' from stage '{stage}' is NOT relevant for activity '{activity['activity']}'")
        # Add custom tools from user responses
        for tool in stage_data.get("custom", []):
            print(f"[DEBUG] Adding custom tool '{tool}' from stage '{stage}'")
            if tool not in relevant_tools["custom"]:
                relevant_tools["custom"].append(tool)
    
    print(f"[DEBUG] Final relevant tools for activity '{activity['activity']}': {relevant_tools}")
    return relevant_tools



@gap_analysis.route("/", methods=["GET", "POST"])
def analyze():
    gap_data = load_json(GAP_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    tools_data = load_json(TOOLS_FILE)
    user_responses = load_json(USER_RESPONSES_FILE)

    # -----------------------------
    # POST: Handle form submission
    # -----------------------------
    if request.method == 'POST':
        selected_tools = request.form.getlist('tools')  # user’s chosen tools
        activity_name = request.form.get('activity')    # which activity we're handling

        print(f"[DEBUG] Processing POST for activity: '{activity_name}' with selected tools: {selected_tools}")
        
        # 1) Find the matching unimplemented activity in gap.json
        for activity in gap_data.get('activities', []):
            if activity.get('activity') == activity_name and activity.get('status') == 'unimplemented':
                # 2) If user explicitly chooses "none", mark it unimplemented_confirmed
                if 'none' in selected_tools:
                    print(f"[DEBUG] User selected 'none' for activity: '{activity_name}'")
                    activity['status'] = 'unimplemented_confirmed'
                    activity['tools'] = []
                    activity['custom'] = []
                    break  # we’re done with this activity
                else:
                    # The user selected at least one tool. Mark activity as implemented.
                    print(f"[DEBUG] Updating activity '{activity_name}' status to implemented")
                    activity['status'] = 'implemented'
                    if 'tools' not in activity:
                        activity['tools'] = []
                    if 'custom' not in activity:
                        activity['custom'] = []

                    # Convert the list of activities to a dictionary for tool selection
                    activity_map = {act["activity"]: act for act in gap_data.get("activities", [])}

                    # 3) For each selected tool: standard or custom
                    for tool in selected_tools:
                        if tool in tools_data:
                            # Standard tool => apply standard tool selection
                            print(f"[DEBUG] Applying standard tool: {tool}")
                            apply_standard_tool_selection(
                                activity_map,       # now a dictionary mapping of activities
                                "Gap Analysis",     # stage label
                                tool,
                                tool_activities
                            )
                            # add to the activity’s standard tools if not already there
                            if tool not in activity['tools']:
                                activity['tools'].append(tool)
                        else:
                            # It's a custom tool
                            print(f"[DEBUG] Adding custom tool: {tool}")
                            if tool not in activity['custom']:
                                activity['custom'].append(tool)

                break  # stop searching the activity list

        # Save updated gap data (if needed, you might want to update gap_data["activities"]
        # with the modified values from activity_map)
        # For example, you can iterate over activity_map and update the list.
        gap_data["activities"] = list(activity_map.values())
        save_json(GAP_FILE, gap_data)
        # redirect to GET => see if more unimplemented remain
        return redirect(url_for('gap_analysis.analyze'))

    # -----------------------------
    # GET: Find next unimplemented
    # -----------------------------
    print("[DEBUG] Processing GET for gap analysis.")
    unimplemented_activities = [activity for activity in gap_data.get('activities', [])
                                if activity.get('status') == "unimplemented"]
    print(f"[DEBUG] Unimplemented activities count: {len(unimplemented_activities)}")
    if unimplemented_activities:
        activity = unimplemented_activities[0]
        relevant_tools = get_relevant_tools(activity, user_responses, tool_activities)
        print(f"[DEBUG] Rendering gap_analysis.html for activity: '{activity.get('activity')}'")
        return render_template(
            "gap_analysis.html",
            activity=activity,
            relevant_tools=relevant_tools
        )
    else:
        print("[DEBUG] No unimplemented activities found. Redirecting to summary.")
        return redirect(url_for("summary.display_summary"))
