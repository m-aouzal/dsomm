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

    # Create pipeline data structure
    pipeline = []
    for item in pipeline_order.get("pipeline", []):
        stage_name = item["stage"]
        stage_tools = []
        
        # Add standard tools
        for tool in item.get("tools", []):
            if tool in user_responses.get("tools", {}).get(stage_name, {}).get("standard", []):
                stage_tools.append({"name": tool, "type": "standard"})
        
        # Add custom tools
        for tool in user_responses.get("tools", {}).get(stage_name, {}).get("custom", []):
            stage_tools.append({"name": tool, "type": "custom"})
        
        pipeline.append((stage_name, stage_tools))

    # Create tool to activities mapping with correct keys
    tool_activities_map = {}
    for tool_name, tool_data in tool_activities.items():
        activities = []
        for activity in tool_data.get("Activities", []):
            activities.append({
                "activity": activity.get("Activity"),  # Changed from "activity" to "Activity"
                "description": activity.get("Description")  # Changed from "description" to "Description"
            })
        tool_activities_map[tool_name] = activities

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
    user_responses = load_json(USER_RESPONSES_FILE)
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)
    pipeline_order = load_json(PIPELINE_ORDER_FILE)
    
    # Create a mapping of tools to their stages
    tool_to_stage = {}
    for item in pipeline_order.get("pipeline", []):
        stage = item["stage"]
        for tool in item.get("tools", []):
            tool_to_stage[tool] = stage
            
    # Group activities by stage
    stages_activities = {}
    for activity in user_responses.get('activities', []):
        # Determine stage based on tools used
        activity_stages = set()
        for tool in activity.get('tools', []):
            if tool in tool_to_stage:
                activity_stages.add(tool_to_stage[tool])
        
        # Add custom tools stages
        for tool in activity.get('custom', []):
            if tool in tool_to_stage:
                activity_stages.add(tool_to_stage[tool])
        
        # If no stage found, put in "Other"
        if not activity_stages:
            activity_stages = {"Other"}
        
        # Add activity to each relevant stage
        for stage in activity_stages:
            if stage not in stages_activities:
                stages_activities[stage] = []
            stages_activities[stage].append(activity)
    
    # Sort stages according to pipeline order
    ordered_stages = [item["stage"] for item in pipeline_order.get("pipeline", [])]
    if "Other" in stages_activities:
        ordered_stages.append("Other")
    
    return render_template(
        "complete_report.html",
        stages_activities=stages_activities,
        ordered_stages=ordered_stages
    )
