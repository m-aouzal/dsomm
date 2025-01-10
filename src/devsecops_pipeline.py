import json
import os

# --- Data Loading and Preprocessing ---

def load_data(tools_file, levels_file, user_responses_file):
    """Loads data from JSON files."""
    with open(tools_file, 'r') as f:
        tools_data = json.load(f)
    with open(levels_file, 'r') as f:
        levels_data = json.load(f)
    if os.path.exists(user_responses_file):
        with open(user_responses_file, 'r') as f:
            user_responses = json.load(f)
    else:
        user_responses = {"selected_tools": [], "stages": [], "activities": {}}
    return tools_data, levels_data, user_responses

def filter_activities(tools_data, levels_data, selected_stages, selected_levels):
    """Filters activities based on selected stages and levels."""
    filtered_activities = {}
    stage_independent_activities = {}

    for tool, details in tools_data.items():
        for activity in details["Activities"]:
            activity_name = activity["Activity"]
            stages = activity["Stages"]

            relevant_levels = [level for level in levels_data if activity_name in levels_data[level]]
            if not any(level in selected_levels for level in relevant_levels):
                continue

            if len(stages) == 1 and stages[0] in selected_stages:
                if activity_name not in filtered_activities:
                    filtered_activities[activity_name] = {"tools": [], "status": "implemented", "stages": stages}
                filtered_activities[activity_name]["tools"].append(tool)

            elif len(stages) > 1:
                if activity_name not in stage_independent_activities:
                    stage_independent_activities[activity_name] = {"tools": [], "status": "pending", "stages": stages}
                stage_independent_activities[activity_name]["tools"].append(tool)

    return filtered_activities, stage_independent_activities

# --- Conflict Resolution and Gap Analysis ---

def resolve_conflicts(stage_independent_activities, user_responses):
    """Resolves activities with multiple tools."""
    for activity_name, details in stage_independent_activities.items():
        if activity_name in user_responses["activities"] and user_responses["activities"][activity_name]["status"] != "pending":
            continue

        print(f"\nActivity: {activity_name} (can be implemented by multiple tools)")
        print("Possible tools:")
        for i, tool in enumerate(details["tools"], 1):
            print(f"{i}. {tool}")
        print(f"{len(details['tools']) + 1}. Add custom tool")
        print(f"{len(details['tools']) + 2}. Skip activity")

        while True:
            try:
                choice = int(input("Select tool(s) (comma-separated numbers) or option: "))
                if 1 <= choice <= len(details["tools"]):
                    selected_tools = [details["tools"][choice - 1]]
                    break
                elif choice == len(details["tools"]) + 1:
                    custom_tool = input("Enter custom tool name: ")
                    selected_tools = [custom_tool]
                    break
                elif choice == len(details["tools"]) + 2:
                    selected_tools = []
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        if selected_tools:
            user_responses["activities"][activity_name] = {"tools": selected_tools, "status": "implemented", "stages": details["stages"]}
        else:
            user_responses["activities"][activity_name] = {"tools": [], "status": "skipped", "stages": details["stages"]}
        
        save_user_responses(user_responses)

def perform_gap_analysis(filtered_activities, stage_independent_activities, user_responses):
    """Identifies and handles unimplemented activities."""
    unimplemented_activities = {}

    for activity_name, details in {**filtered_activities, **stage_independent_activities}.items():
        if activity_name not in user_responses["activities"] or user_responses["activities"][activity_name]["status"] == "skipped":
            unimplemented_activities[activity_name] = details

    for activity_name, details in unimplemented_activities.items():
        print(f"\nUnimplemented Activity: {activity_name}")
        if details['tools']:
            print("Possible tools:")
            for i, tool in enumerate(details["tools"], 1):
                print(f"{i}. {tool}")
            print(f"{len(details['tools']) + 1}. Add custom tool")
        else:
             print("Add custom tool")
        print(f"{len(details['tools']) + 2 if details['tools'] else 1}. Mark as explicitly unimplemented")

        while True:
            try:
                choice = int(input("Select tool or option: "))
                if details['tools'] and 1 <= choice <= len(details["tools"]):
                    selected_tool = details["tools"][choice - 1]
                    user_responses["activities"][activity_name] = {"tools": [selected_tool], "status": "implemented", "stages": details["stages"]}
                    break
                elif choice == len(details["tools"]) + 1 or (not details['tools'] and choice == 1):
                    custom_tool = input("Enter custom tool name: ")
                    user_responses["activities"][activity_name] = {"tools": [custom_tool], "status": "implemented", "stages": details["stages"]}
                    break
                elif choice == (len(details["tools"]) + 2 if details['tools'] else 2):
                    user_responses["activities"][activity_name] = {"tools": [], "status": "unimplemented", "stages": details["stages"]}
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        save_user_responses(user_responses)

# --- User Input Handling ---

def get_user_input(tools_data, levels_data):
    """Gets initial user input for stages and tools."""
    print("\nAvailable Stages:")
    stages = set()
    for tool, details in tools_data.items():
        for activity in details["Activities"]:
            stages.update(activity["Stages"])
    stages = list(stages)
    for i, stage in enumerate(stages, 1):
        print(f"{i}. {stage}")

    while True:
        try:
            selected_stages_indices = input("Select stage(s) (comma-separated numbers): ").split(',')
            selected_stages = [stages[int(index) - 1] for index in selected_stages_indices if 1 <= int(index) <= len(stages)]
            if not selected_stages:
                raise ValueError("No valid stages selected.")
            break
        except (ValueError, IndexError):
            print("Invalid input. Please enter valid stage numbers separated by commas.")

    print("\nAvailable Levels:")
    for i, level in enumerate(levels_data.keys(), 1):
        print(f"{i}. {level}")

    while True:
        try:
            selected_levels_indices = input("Select level(s) (comma-separated numbers): ").split(',')
            selected_levels = [list(levels_data.keys())[int(index) - 1] for index in selected_levels_indices if 1 <= int(index) <= len(levels_data)]
            if not selected_levels:
                raise ValueError("No valid levels selected.")
            break
        except (ValueError, IndexError):
            print("Invalid input. Please enter valid level numbers separated by commas.")

    return selected_stages, selected_levels

# --- File Saving ---

def save_user_responses(user_responses, filename="user_responses.json"):
    """Saves user responses to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(user_responses, f, indent=4)

# --- Report Generation ---

def generate_report(user_responses):
    """Generates a summary report."""
    print("\n--- DevSecOps Pipeline Summary ---")
    print("\nImplemented Activities:")
    for activity_name, details in user_responses["activities"].items():
        if details["status"] == "implemented":
            print(f"- {activity_name}: {', '.join(details['tools'])}")

    print("\nSkipped Activities:")
    for activity_name, details in user_responses["activities"].items():
        if details["status"] == "skipped":
            print(f"- {activity_name}")

    print("\nExplicitly Unimplemented Activities:")
    for activity_name, details in user_responses["activities"].items():
        if details["status"] == "unimplemented":
            print(f"- {activity_name}")

# --- Main Script ---

if __name__ == "__main__":
    TOOLS_FILE = "tools_activities_mapping_with_details.json"
    LEVELS_FILE = "level_activities.json"
    USER_RESPONSES_FILE = "user_responses.json"

    tools_data, levels_data, user_responses = load_data(TOOLS_FILE, LEVELS_FILE, USER_RESPONSES_FILE)

    selected_stages, selected_levels = get_user_input(tools_data, levels_data)
    user_responses["stages"] = selected_stages

    filtered_activities, stage_independent_activities = filter_activities(tools_data, levels_data, selected_stages, selected_levels)

    resolve_conflicts(stage_independent_activities, user_responses)

    while True:
        perform_gap_analysis(filtered_activities, stage_independent_activities, user_responses)

        remaining_conflicts = any(details["status"] == "pending" for details in stage_independent_activities.values())
        remaining_gaps = any(activity_name not in user_responses["activities"] or user_responses["activities"][activity_name]["status"] not in ["implemented", "unimplemented"]
                             for activity_name in {**filtered_activities, **stage_independent_activities})

        if not remaining_conflicts and not remaining_gaps:
            break  # Exit loop if no more conflicts or gaps

        resolve_conflicts(stage_independent_activities, user_responses)

    generate_report(user_responses)
