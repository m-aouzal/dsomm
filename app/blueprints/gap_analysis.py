from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os

gap_analysis = Blueprint("gap_analysis", __name__)

DATA_FOLDER = "./data"
GAP_FILE = os.path.join(DATA_FOLDER, "gap.json")
USER_RESPONSES_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")
CUSTOM_TOOLS_FILE = os.path.join(DATA_FOLDER, "custom_tools.json")
LEVEL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "level_activities.json")

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
def analyze_gaps():
    # Load necessary data
    user_responses = load_json(USER_RESPONSES_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    level_activities = load_json(LEVEL_ACTIVITIES_FILE)
    custom_tools = load_json(CUSTOM_TOOLS_FILE)
    
    print("[DEBUG] Starting gap analysis...")
    
    activities = user_responses.get("activities", [])
    
    if request.method == "POST":
        activity_name = request.form.get("activity")
        chosen_tools = request.form.getlist("tools")
        custom_tool_names = request.form.getlist("custom_tool")
        
        # Update activity status
        for activity in activities:
            if activity["activity"] == activity_name:
                if "none" in chosen_tools:
                    activity["status"] = "unimplemented_confirmed"
                    activity["tools"] = {}
                    activity["custom"] = []
                else:
                    activity["status"] = "implemented"
                    activity["tools"] = {tool: "checked" for tool in chosen_tools if tool != "none"}
                    
                    # Handle custom tools
                    activity["custom"] = []
                    for tool_name in custom_tool_names:
                        tool_name = tool_name.strip()
                        if tool_name:
                            activity["tools"][tool_name] = "checked"
                            activity["custom"].append(tool_name)
                            
                            # Update custom_tools file
                            if activity_name not in custom_tools:
                                custom_tools[activity_name] = []
                            if tool_name not in custom_tools[activity_name]:
                                custom_tools[activity_name].append(tool_name)
                break
        
        # Save updates
        user_responses["activities"] = activities
        save_json(USER_RESPONSES_FILE, user_responses)
        save_json(CUSTOM_TOOLS_FILE, custom_tools)
        
        return redirect(url_for("gap_analysis.analyze_gaps"))
    
    # Find first unimplemented activity
    unimplemented = None
    checked_activities = []
    
    for activity in activities:
        if activity.get("status") == "unimplemented":
            unimplemented = activity
            break
        elif activity.get("status") == "checked":
            checked_activities.append(activity)
    
    # Handle different scenarios
    if not unimplemented and checked_activities:
        return render_template(
            "checking.html",
            activities=checked_activities
        )
    
    if not unimplemented:
        return redirect(url_for("summary.display_summary"))
    
    # Get relevant tools for the unimplemented activity
    relevant_tools = get_relevant_tools(unimplemented, user_responses, tool_activities)
    
    # Get activity details
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