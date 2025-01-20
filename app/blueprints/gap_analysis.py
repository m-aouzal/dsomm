from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
from .utils import apply_standard_tool_selection_gap_analysis

gap_analysis = Blueprint("gap_analysis", __name__)

DATA_FOLDER = "./data"
GAP_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
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
        "custom": []
    }
    
    print(f"[DEBUG] Getting relevant tools for activity: '{activity['activity']}'")
    
    # Get standard tools that can implement this activity
    for tool_name, tool_data in tool_activities.items():
        for tool_activity in tool_data.get("Activities", []):
            if tool_activity.get("Activity") == activity["activity"]:
                print(f"[DEBUG] Found standard tool '{tool_name}' for activity '{activity['activity']}'")
                if tool_name not in relevant_tools["standard"]:
                    relevant_tools["standard"].append(tool_name)
    
    # Get only custom tools from user's previous selections
    for stage, stage_data in user_responses.get("tools", {}).items():
        print(f"[DEBUG] Checking user tools for stage: '{stage}'")
        for tool in stage_data.get("custom", []):
            print(f"[DEBUG] Adding custom tool '{tool}' from stage '{stage}'")
            if tool not in relevant_tools["custom"]:
                relevant_tools["custom"].append(tool)
    
    print(f"[DEBUG] Final relevant tools for activity '{activity['activity']}': {relevant_tools}")
    return relevant_tools

@gap_analysis.route("/", methods=["GET", "POST"])
def analyze():
    user_responses = load_json(USER_RESPONSES_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    tools_data = load_json(TOOLS_FILE)

    if request.method == 'POST':
        selected_tools = request.form.getlist('tools')
        custom_tools = request.form.getlist('custom_tools')  # Get custom tools
        new_custom_tool = request.form.get('newCustomTool', '').strip()  # Get new custom tool
        activity_name = request.form.get('activity')

        print(f"[DEBUG] Processing POST for activity: '{activity_name}'")
        print(f"[DEBUG] Selected standard tools: {selected_tools}")
        print(f"[DEBUG] Custom tools: {custom_tools}")
        print(f"[DEBUG] New custom tool: {new_custom_tool}")

        # Initialize activity_map
        activity_map = {}
        for act in user_responses.get("activities", []):
            act_copy = act.copy()
            if not isinstance(act_copy.get('tools', []), list):
                act_copy['tools'] = []
            activity_map[act["activity"]] = act_copy

        changes_made = False
        for activity in user_responses.get('activities', []):
            if activity.get('activity') == activity_name and activity.get('status') == 'unimplemented':
                relevant_tools = get_relevant_tools(activity, user_responses, tool_activities)
                
                if not relevant_tools['standard']:
                    print(f"[DEBUG] No standard tools for activity: '{activity_name}', marking as policy")
                    activity['status'] = 'policy'
                    activity['tools'] = []
                    activity['custom'] = []
                    changes_made = True
                    break
                
                if 'none' in selected_tools:
                    activity['status'] = 'unimplemented_confirmed'
                    activity['tools'] = []
                    activity['custom'] = []
                    changes_made = True
                else:
                    # Handle standard tools
                    for tool in selected_tools:
                        if tool in tools_data:
                            if tool not in activity['tools']:
                                activity['tools'].append(tool)
                                print(f"[DEBUG] Added standard tool: {tool}")

                    # Handle custom tools
                    activity['custom'] = activity.get('custom', [])
                    for tool in custom_tools:
                        if tool not in activity['custom']:
                            activity['custom'].append(tool)
                            print(f"[DEBUG] Added existing custom tool: {tool}")

                    # Handle new custom tool
                    if new_custom_tool and new_custom_tool not in activity['custom']:
                        activity['custom'].append(new_custom_tool)
                        print(f"[DEBUG] Added new custom tool: {new_custom_tool}")

                    activity['status'] = 'implemented'
                    changes_made = True

                    # Apply standard tools to other activities
                    for tool in [t for t in selected_tools if t in tools_data]:
                        apply_standard_tool_selection_gap_analysis(
                            tool,
                            tool_activities
                        )
                break

        if changes_made:
            print("[DEBUG] Saving changes to user_responses.json")
            user_responses["activities"] = list(activity_map.values())
            save_json(USER_RESPONSES_FILE, user_responses)

        return redirect(url_for('gap_analysis.analyze'))

    # -----------------------------
    # GET: Find next unimplemented
    # -----------------------------
    print("[DEBUG] Processing GET for gap analysis.")
    unimplemented = None
    changes_made = False  # Track if we made any changes
    
    for activity in user_responses.get('activities', []):
        if activity.get('status') == 'unimplemented':
            relevant_tools = get_relevant_tools(activity, user_responses, tool_activities)
            print(f"[DEBUG] Checking activity '{activity['activity']}' - relevant tools: {relevant_tools}")
            
            if not relevant_tools['standard']:
                print(f"[DEBUG] No standard tools for activity: '{activity['activity']}', marking as policy")
                activity['status'] = 'policy'
                activity['tools'] = []
                activity['custom'] = []
                changes_made = True  # Mark that we made changes
                continue
            
            unimplemented = activity
            break
    
    # Save changes if any activities were marked as policy
    if changes_made:
        print("[DEBUG] Saving changes to user_responses.json after marking policy activities")
        save_json(USER_RESPONSES_FILE, user_responses)
    
    if not unimplemented:
        # Check for checked activities
        to_review = [a for a in user_responses['activities'] if a['status'] == 'checked']
        if to_review:
            return render_template('checking.html', activities=to_review)
        return redirect(url_for('summary.display_summary'))
    
    relevant_tools = get_relevant_tools(unimplemented, user_responses, tool_activities)
    
    return render_template('gap_analysis.html',
                         activity=unimplemented,
                         relevant_tools=relevant_tools)
