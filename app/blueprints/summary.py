from flask import Blueprint, render_template, request, redirect, url_for
import os
import json
from .utils import load_json, USER_RESPONSES_FILE

summary = Blueprint("summary", __name__)

DATA_FOLDER = "./data"
PIPELINE_ORDER_FILE = os.path.join(DATA_FOLDER, "pipeline_order.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")

@summary.route("/")
def display_summary():
    """Display summary of selected tools and activities."""
    user_responses = load_json(USER_RESPONSES_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    pipeline_order = load_json(PIPELINE_ORDER_FILE)

    # Create tool to activities mapping with correct keys
    tool_activities_map = {}
    for tool_name, tool_data in tool_activities.items():
        activities = []
        for activity in tool_data.get("Activities", []):
            activities.append({
                "activity": activity.get("Activity"),
                "description": activity.get("Description")
            })
        # Only add tools that have activities
        if activities:
            tool_activities_map[tool_name] = activities

    # Create pipeline data structure with filtering
    pipeline = []
    for item in pipeline_order.get("pipeline", []):
        stage_name = item["stage"]
        stage_tools = []
        
        # Add standard tools that have activities
        for tool in item.get("tools", []):
            if (tool in user_responses.get("tools", {}).get(stage_name, {}).get("standard", []) and
                tool in tool_activities_map):
                stage_tools.append({"name": tool, "type": "standard"})
        
        # Add custom tools that have activities
        for tool in user_responses.get("tools", {}).get(stage_name, {}).get("custom", []):
            if tool in tool_activities_map:
                stage_tools.append({"name": tool, "type": "custom"})
        
        # Only add stages that have tools with activities
        if stage_tools:
            pipeline.append((stage_name, stage_tools))

    # Sort activities by status
    activities = user_responses.get('activities', [])
    
    # Normalize unimplemented_confirmed to unimplemented
    for activity in activities:
        if activity.get('status') == 'unimplemented_confirmed':
            activity['status'] = 'unimplemented'
    
    # Group activities by status
    implemented = [a for a in activities if a.get('status') == 'implemented']
    policy = [a for a in activities if a.get('status') == 'policy']
    unimplemented = [a for a in activities if a.get('status') == 'unimplemented']
    
    # Combine in desired order
    ordered_activities = implemented + policy + unimplemented

    return render_template(
        "summary.html",
        pipeline=pipeline,
        tool_activities_map=tool_activities_map,
        responses=user_responses,
        ordered_activities=ordered_activities
    )

@summary.route("/complete-report")
def complete_report():
    print("[DEBUG] Starting complete_report route")
    
    user_responses = load_json(USER_RESPONSES_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    pipeline_order = load_json(PIPELINE_ORDER_FILE)
    dsomm = load_json(os.path.join(DATA_FOLDER, "dsomm.json"))
    
    # Default fields that are always shown and not toggleable
    default_fields = ['Dimension', 'Sub Dimension', 'Activity', 'Description']
    
    # Additional fields that can be toggled
    available_fields = [
        'Level',
        'Risk',
        'Measure',
        'Knowledge',
        'Resources',
        'Time',
        'Usefulness',
        'SAMM',
        'ISO 27001:2017',
        'ISO 27001:2022'
    ]
    
    print(f"[DEBUG] Default fields: {default_fields}")
    print(f"[DEBUG] Available toggle fields: {available_fields}")
    
    # Initialize stages from pipeline order
    ordered_stages = [item["stage"] for item in pipeline_order.get("pipeline", [])]
    stages_activities = {stage: [] for stage in ordered_stages}
    stages_activities["Policy"] = []
    stages_activities["Unimplemented"] = []
    
    print(f"[DEBUG] Processing {len(user_responses.get('activities', []))} activities")
    
    # Enrich and organize activities
    for activity in user_responses.get('activities', []):
        print(f"[DEBUG] Processing activity: {activity.get('activity')}")
        
        # Normalize the status
        if activity.get('status') == 'unimplemented_confirmed':
            activity['status'] = 'unimplemented'
        
        # Enrich from the DSOMM data
        for dsomm_activity in dsomm:
            if dsomm_activity.get("Activity") == activity.get("activity"):
                print(f"[DEBUG] Found matching DSOMM activity")
                activity.update({
                    "Dimension": dsomm_activity.get("Dimension"),
                    "Sub Dimension": dsomm_activity.get("Sub Dimension"),
                    "Activity": dsomm_activity.get("Activity"),
                    "Description": dsomm_activity.get("Description"),
                    "Level": dsomm_activity.get("Level"),
                    "Risk": dsomm_activity.get("Risk"),
                    "Measure": dsomm_activity.get("Measure"),
                    "Knowledge": dsomm_activity.get("Knowledge"),
                    "Resources": dsomm_activity.get("Resources"),
                    "Time": dsomm_activity.get("Time"),
                    "Usefulness": dsomm_activity.get("Usefulness"),
                    "SAMM": dsomm_activity.get("SAMM"),
                    "ISO 27001:2017": dsomm_activity.get("ISO 27001:2017"),
                    "ISO 27001:2022": dsomm_activity.get("ISO 27001:2022")
                })
                break
        
        # Assign activity to appropriate stage
        if activity.get('status') == 'policy':
            print(f"[DEBUG] Adding to Policy stage")
            stages_activities["Policy"].append(activity)
        elif activity.get('status') == 'unimplemented':
            print(f"[DEBUG] Adding to Unimplemented stage")
            stages_activities["Unimplemented"].append(activity)
        else:
            stage_found = False
            for stage in ordered_stages:
                stage_tools = user_responses.get("tools", {}).get(stage, {})
                activity_tools = set(activity.get("tools", []) + activity.get("custom", []))
                stage_all_tools = set(stage_tools.get("standard", []) + stage_tools.get("custom", []))
                
                if activity_tools & stage_all_tools:
                    print(f"[DEBUG] Adding to stage {stage}")
                    stages_activities[stage].append(activity)
                    stage_found = True
                    break
            
            if not stage_found and ordered_stages:
                print(f"[DEBUG] No stage found, adding to {ordered_stages[0]}")
                stages_activities[ordered_stages[0]].append(activity)
    
    # Remove empty stages
    stages_activities = {k: v for k, v in stages_activities.items() if v}
    
    # Update ordered_stages to only include stages with activities
    ordered_stages = [stage for stage in ordered_stages if stage in stages_activities]
    if stages_activities.get("Policy"):
        ordered_stages.append("Policy")
    if stages_activities.get("Unimplemented"):
        ordered_stages.append("Unimplemented")
    
    print(f"[DEBUG] Final stages with activities: {list(stages_activities.keys())}")
    print(f"[DEBUG] Number of activities per stage: {[(k, len(v)) for k, v in stages_activities.items()]}")
    
    return render_template(
        "complete_report.html",
        stages_activities=stages_activities,
        ordered_stages=ordered_stages,
        available_fields=available_fields,
        default_fields=default_fields,
        all_fields=default_fields + available_fields  # Add this for template iteration
    )
