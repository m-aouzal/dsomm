import json

def apply_standard_tool_selection(activity_status, stage, tool_name, tool_activities_data):
    """Applies standard tool selection to activities."""
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

        # Skip if activity is already implemented or policy
        current_status = act_item.get("status")
        if current_status in ["implemented", "policy"]:
            print(f"[DEBUG] Skipping activity '{act_name}' as it is already {current_status}")
            continue

        # Initialize tools as list if needed
        if 'tools' not in act_item:
            act_item['tools'] = []

        # Add the tool to the activity's tools list
        if tool_name not in act_item["tools"]:
            act_item["tools"].append(tool_name)
            print(f"[DEBUG] Added tool '{tool_name}' to activity '{act_name}'")

        # Update activity status based on existing status
        if act_item["status"] == "unimplemented":
            act_item["status"] = "checked"
            print(f"[DEBUG] Changed status from 'unimplemented' to 'checked' for '{act_name}'")
        elif act_item["status"] == "checked":
            act_item["status"] = "temporary"
            print(f"[DEBUG] Changed status from 'checked' to 'temporary' for '{act_name}'")

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

        if "custom" not in act_item:
            act_item["custom"] = []
        if tool_name not in act_item["custom"]:
            act_item["custom"].append(tool_name)

        act_item["tools"].append(tool_name)

        if act_item["status"] == "unimplemented":
            act_item["status"] = "checked"
        elif act_item["status"] in ["checked", "implemented"] and len(act_item["tools"]) > 0:
            act_item["status"] = "temporary"

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
        for act_obj in lvl_activities:
            activities.append({
                "activity": act_obj.get("Activity", f"Activity-L{lvl}"),
                "description": act_obj.get("Description", ""),
                "status": "unimplemented",
                "custom": [],
                "tools": []
            })
    return activities

def prepare_activities_for_gap_analysis(user_responses, config_data):
    """Prepares activity data for Gap Analysis with separate handling of implemented and policy activities."""
    print("[DEBUG] Starting preparation for gap analysis")
    
    # Extract configuration data
    level_activities_data = config_data["level_activities"]
    tool_activities_data = config_data["tool_activities"]
    stage_defaults = config_data["stage_defaults"]
    policies_data = config_data.get("policies", {})
    
    chosen_level = user_responses["selected_level"]
    chosen_stages = user_responses["stages"]
    stage_tools = user_responses["tools"]
    
    print(f"[DEBUG] Processing level {chosen_level} with {len(chosen_stages)} stages")

    # 1. Get all activities for the chosen level
    activities = get_activities_for_level(chosen_level, level_activities_data)
    activities_map = {act["activity"]: act for act in activities}
    print(f"[DEBUG] Initial activities count: {len(activities_map)}")

    # 2. Apply tool selections to ALL activities
    print("[DEBUG] Applying tool selections to all activities")
    for stage in chosen_stages:
        stage_data = stage_tools.get(stage, {"standard": [], "custom": []})
        
        # Apply standard tools
        for tool in stage_data.get("standard", []):
            apply_standard_tool_selection(activities_map, stage, tool, tool_activities_data)
        
        # Apply custom tools
        for tool in stage_data.get("custom", []):
            apply_custom_tool_selection(activities_map, stage, tool, stage_defaults)

    # 3. Separate implemented activities
    implemented_activities = []
    for activity in user_responses.get("activities", []):
        if activity.get("status") == "implemented":
            implemented_activities.append(activity.copy())
            if activity["activity"] in activities_map:
                del activities_map[activity["activity"]]
            print(f"[DEBUG] Separated implemented activity: {activity['activity']}")

    # 4. Separate policy activities (cumulative based on chosen level)
    policy_activities = []
    try:
        max_level = int(chosen_level)
        for level in range(1, max_level + 1):
            level_policies = policies_data.get(str(level), [])
            print(f"[DEBUG] Processing policies for level {level}: found {len(level_policies)} policies")
            
            for policy in level_policies:
                policy_name = policy.get("Activity")
                if not policy_name:
                    print(f"[WARNING] Found policy without Activity name in level {level}")
                    continue
                    
                if policy_name in activities_map:
                    policy_activity = activities_map[policy_name].copy()
                    policy_activity["status"] = "policy"
                    policy_activity["description"] = policy.get("Description", policy_activity.get("description", ""))
                    policy_activities.append(policy_activity)
                    del activities_map[policy_name]
                    print(f"[DEBUG] Separated policy activity: {policy_name} from level {level}")
                else:
                    print(f"[DEBUG] Policy activity {policy_name} from level {level} not found or already processed")
    except ValueError:
        print(f"[ERROR] Invalid security level format: {chosen_level}")
        return False

    # 5. The remaining activities in activities_map are the modified ones
    modified_activities = list(activities_map.values())
    print(f"[DEBUG] Modified activities count: {len(modified_activities)}")

    # 6. Combine all activities in the desired order
    gap_analysis_activities = (
        implemented_activities +  # Already implemented activities (unchanged)
        modified_activities +     # Modified activities (with tool selections applied)
        policy_activities        # Policy activities
    )

    # 7. Prepare and save gap data
    gap_data = {
        "selected_level": chosen_level,
        "stages": chosen_stages,
        "tools": stage_tools,
        "activities": gap_analysis_activities
    }
    
    print("[DEBUG] Final activity counts:")
    print(f"  - Implemented: {len(implemented_activities)}")
    print(f"  - Modified: {len(modified_activities)}")
    print(f"  - Policy: {len(policy_activities)}")
    print(f"  - Total: {len(gap_analysis_activities)}")
    
    try:
        with open("./data/gap.json", "w") as f:
            json.dump(gap_data, f, indent=4, ensure_ascii=False)
        print(f"[DEBUG] Successfully saved gap.json")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save gap.json: {str(e)}")
        return False
