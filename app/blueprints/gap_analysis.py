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
    
    # Get standard tools that can implement this activity
    for tool_name, tool_data in tool_activities.items():
        for tool_activity in tool_data.get("Activities", []):
            if tool_activity.get("Activity") == activity["activity"]:
                relevant_tools["standard"].append(tool_name)
    
    # Get user's previously selected tools
    for stage_data in user_responses.get("tools", {}).values():
        # Add standard tools
        for tool in stage_data.get("standard", []):
            if tool in relevant_tools["standard"] and tool != "none":
                relevant_tools["user_selected"].append(tool)
        # Add custom tools
        for tool in stage_data.get("custom", []):
            if tool not in relevant_tools["custom"]:
                relevant_tools["custom"].append(tool)
    
    return relevant_tools

@gap_analysis.route("/", methods=["GET", "POST"])
def analyze():
    # Load data once at the start
    gap_data = load_json(GAP_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    level_activities = load_json(LEVEL_ACTIVITIES_FILE)
    tools_data = load_json(TOOLS_FILE)
    
    if request.method == 'POST':
        selected_tools = request.form.getlist('tools')
        activity_name = request.form.get('activity')
        
        # Find the activity in gap.json
        for activity in gap_data.get('activities', []):
            if activity.get('activity') == activity_name:
                # Only process if activity is unimplemented or checked
                if activity.get('status') in ['unimplemented', 'checked']:
                    # Separate standard and custom tools
                    standard_tools = []
                    custom_tools = []
                    
                    for tool in selected_tools:
                        if tool == 'none':
                            # Handle none selection
                            activity['status'] = 'unimplemented_confirmed'
                            activity['tools'] = []
                            activity['custom'] = []
                            break
                        elif tool in tools_data:
                            # Apply standard tool selection only for standard tools
                            print(f"[DEBUG] Applying standard tool: {tool}")
                            apply_standard_tool_selection(
                                gap_data.get('activities', []),
                                "Gap Analysis",
                                tool,
                                tool_activities
                            )
                            standard_tools.append(tool)
                        else:
                            # Handle custom tools separately
                            print(f"[DEBUG] Adding custom tool: {tool}")
                            custom_tools.append(tool)
                    
                    if 'none' not in selected_tools:
                        activity['status'] = 'checked'
                        activity['tools'] = standard_tools
                        # Append new custom tools to existing ones
                        if 'custom' not in activity:
                            activity['custom'] = []
                        activity['custom'].extend(custom_tools)
                
                break
        
        # Save updated gap data
        save_json(GAP_FILE, gap_data)
        return redirect(url_for('gap_analysis.analyze'))
    
    # GET request handling - use already loaded data
    unimplemented = None
    checked_activities = []
    
    for activity in gap_data.get('activities', []):
        if activity.get('status') == "unimplemented":
            unimplemented = activity
            break
        elif activity.get('status') == "checked":
            checked_activities.append(activity)
    
    if not unimplemented and checked_activities:
        return render_template(
            "checking.html",
            activities=checked_activities
        )
    
    if not unimplemented:
        return redirect(url_for("summary.display_summary"))
    
    # For getting relevant tools, we still need user_responses to show previously selected tools
    user_responses = load_json(USER_RESPONSES_FILE)
    relevant_tools = get_relevant_tools(unimplemented, user_responses, tool_activities)
    
    activity_details = None
    for level_data in level_activities.values():
        for activity in level_data:
            if activity.get("activity") == unimplemented["activity"]:
                activity_details = activity
                break
    
    print(f"[DEBUG] Analyzing activity: {unimplemented['activity']}")
    print(f"[DEBUG] Relevant tools: {relevant_tools}")
    
    return render_template(
        "gap_analysis.html",
        activity=unimplemented,
        activity_details=activity_details,
        relevant_tools=relevant_tools
    )