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
    """
    Generates a final DevSecOps pipeline report in a stage-by-stage order,
    including logic to determine where custom tools belong.
    """
    # ------------------------------------------------------------------------------
    # 1. Load needed data
    # ------------------------------------------------------------------------------
    user_responses = load_json(USER_RESPONSES_FILE)
    pipeline_order = load_json(PIPELINE_ORDER_FILE)   # e.g. ["Planning", "Source Code Mgmt", "Build", ...]
    tool_activities_data = load_json(TOOL_ACTIVITIES_FILE)  # e.g. { "Git": { Activities: [...], ... }, ... }

    activities = user_responses.get("activities", [])
    chosen_stages = user_responses.get("stages", [])
    selected_level = user_responses.get("selected_level", "N/A")

    # A dict of stages -> { 'standard': [...], 'custom': [...] }
    # Possibly from user_responses["tools"] or from your own approach
    stages_tools = user_responses.get("tools", {})

    # ------------------------------------------------------------------------------
    # 2. Create a "stage_index" mapping from pipeline_order to help sorting
    # ------------------------------------------------------------------------------
    stage_index_map = {}
    for idx, st_name in enumerate(pipeline_order):
        stage_index_map[st_name] = idx

    # ------------------------------------------------------------------------------
    # 3. Gather "standard" tools with direct stage references
    #    We'll store them in a structure: tool_stage_map = { "Git": "Source Code Mgmt", ... }
    # ------------------------------------------------------------------------------
    tool_stage_map = {}
    for stage_name, st_data in stages_tools.items():
        # If stage_name is not in the chosen_stages, skip
        if stage_name not in chosen_stages:
            continue

        # st_data could look like { "standard": ["Git","GitHub"], "custom": ["MyScanner"] }
        # Let's fill out the standard ones first
        for std_tool in st_data.get("standard", []):
            tool_stage_map[std_tool] = stage_name

    # ------------------------------------------------------------------------------
    # 4. Logic for "custom tools":
    #    We find each custom tool (from user_responses or from the activities)
    #    Then we check which stage it belongs to, by "majority logic".
    # ------------------------------------------------------------------------------
    custom_tool_stage_map = {}
    
    # A function to figure out the "majority" stage for a custom tool
    def find_stage_for_custom_tool(custom_tool_name):
        """
        - Look at the activities that mention this custom tool in 'activities'.
        - For each of these activities, see which standard tools can also implement that activity.
        - Collect the known stage of those standard tools from 'tool_stage_map'.
        - Whichever stage appears the most is assigned. If no majority, pick the first found.
        - If still ambiguous, default to '???'
        """
        # gather all relevant activities for this custom tool
        relevant_activities = [act for act in activities
                               if custom_tool_name in act.get("custom", [])]
        # collect the stages
        stage_counts = {}

        for act_item in relevant_activities:
            # find standard tools that can also implement this activity
            # "tools" field => standard tool
            for std_tool in act_item.get("tools", []):
                if std_tool in tool_stage_map:
                    st = tool_stage_map[std_tool]
                    stage_counts[st] = stage_counts.get(st, 0) + 1

        if not stage_counts:
            # no standard tool found => no majority => return "???"
            return "???"

        # find the stage with the highest count
        sorted_counts = sorted(stage_counts.items(), key=lambda x: x[1], reverse=True)
        top_stage, _ = sorted_counts[0]
        return top_stage

    # gather all custom tools from user_responses
    # they might appear in user_responses["tools"][stage]["custom"] or in activities' "custom"
    # let's do both
    custom_tools_set = set()
    for stage_name, st_data in stages_tools.items():
        for c_tool in st_data.get("custom", []):
            custom_tools_set.add(c_tool)

    # also from the "activities" data
    for act_item in activities:
        for c_tool in act_item.get("custom", []):
            custom_tools_set.add(c_tool)

    # Now find the stage for each custom tool
    for c_tool in custom_tools_set:
        # if it's already in tool_stage_map, skip (rare but might happen)
        if c_tool in tool_stage_map:
            continue

        # use the majority logic
        assigned_stage = find_stage_for_custom_tool(c_tool)
        custom_tool_stage_map[c_tool] = assigned_stage
        tool_stage_map[c_tool] = assigned_stage  # so we have a unified map

    # ------------------------------------------------------------------------------
    # 5. Build a final ordered data structure: stages -> list of tools
    # ------------------------------------------------------------------------------
    # let's create a dictionary: final_stages = { stage_name: [ {name, type}, ... ] }
    final_stages = {}
    for stg in chosen_stages:
        final_stages[stg] = []

    # insert known tools
    # standard ones from stages_tools
    for stg_name, st_data in stages_tools.items():
        if stg_name not in final_stages:
            continue
        for std_tool in st_data.get("standard", []):
            final_stages[stg_name].append({
                "name": std_tool,
                "type": "standard"
            })
        for c_tool in st_data.get("custom", []):
            final_stages[stg_name].append({
                "name": c_tool,
                "type": "custom"
            })

    # add custom tools discovered via majority logic that might not be in the original stage data
    for c_tool, stg_assigned in custom_tool_stage_map.items():
        # If that stage wasn't chosen or is ???, skip or place it somewhere
        if stg_assigned not in chosen_stages:
            # up to you how to handle tools assigned to a stage the user didn't pick
            # maybe final_stages.setdefault("???", [])
            # final_stages["???"].append(...)
            continue
        # if not already in final_stages:
        found = False
        for t in final_stages[stg_assigned]:
            if t["name"] == c_tool:
                found = True
                break
        if not found:
            final_stages[stg_assigned].append({
                "name": c_tool,
                "type": "custom"
            })

    # Sort each stage's tools alphabetically by "name"
    for stg_name in final_stages:
        final_stages[stg_name].sort(key=lambda x: x["name"].lower())

    # Sort stages by pipeline_order
    # We'll produce a list of (stage_name, tools_list)
    ordered_pipeline = sorted(
        final_stages.items(),
        key=lambda item: stage_index_map.get(item[0], 9999)
    )

    # ------------------------------------------------------------------------------
    # 6. Prepare data to show which activities each tool implements
    #    We'll do a quick lookup: tool -> list of activities
    # ------------------------------------------------------------------------------
    tool_activities_map = {}
    for act_item in activities:
        # any standard tool in act_item["tools"]
        for std_tool in act_item.get("tools", []):
            if std_tool not in tool_activities_map:
                tool_activities_map[std_tool] = []
            tool_activities_map[std_tool].append(act_item)

        # any custom tool in act_item["custom"]
        for c_tool in act_item.get("custom", []):
            if c_tool not in tool_activities_map:
                tool_activities_map[c_tool] = []
            tool_activities_map[c_tool].append(act_item)

    # ------------------------------------------------------------------------------
    # 7. Render the summary.html
    # ------------------------------------------------------------------------------
    return render_template(
        "summary.html",
        selected_level=selected_level,
        pipeline=ordered_pipeline,         # [ (stage_name, [ {name,type}, ... ] ), ... ]
        tool_activities_map=tool_activities_map,
        user_activities=activities
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
