from flask import Blueprint, render_template, request, redirect, url_for
import json
import os
from .utils import load_json, save_json, USER_RESPONSES_FILE, get_relevant_tools

checking = Blueprint("checking", __name__)

DATA_FOLDER = "./data"
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")

@checking.route("/", methods=["GET", "POST"])
def verify_checked_activities():
    """
    This route handles activities with 'status' == 'checked'.
    For each activity, the user may select from:
      - Global custom tools ("My Tools") – the custom tools gathered from all stages.
      - Relevant tools ("More Tools") – as returned by get_relevant_tools, filtered to remove duplicates with My Tools.
    The user may also add a new custom tool.
    """
    # Load data
    user_responses = load_json(USER_RESPONSES_FILE)
    activities_list = user_responses.get("activities", [])
    stage_tools = user_responses.get("tools", {})
    tool_activities = load_json(TOOL_ACTIVITIES_FILE)

    # 1. Gather activities with status "checked"
    checked_activities = [act for act in activities_list if act.get("status") == "checked"]

    # 2. Gather global custom tools from user_responses (for My Tools)
    all_custom_tools = set()
    for stage, data in stage_tools.items():
        for tool in data.get("custom", []):
            all_custom_tools.add(tool)
    my_custom_tools = sorted(list(all_custom_tools))

    # 3. For each checked activity, compute and filter relevant tools
    activity_relevant_tools = {}
    for act in checked_activities:
        relevant_tools = get_relevant_tools(act, user_responses, tool_activities)
        
        # Filter out tools that are already in my_custom_tools
        filtered_tools = {
            "standard": [t for t in relevant_tools.get("standard", []) if t not in my_custom_tools],
            "custom": [t for t in relevant_tools.get("custom", []) if t not in my_custom_tools],
            "user_selected": relevant_tools.get("user_selected", [])
        }
        
        activity_relevant_tools[act["activity"]] = filtered_tools

    if request.method == "POST":
        # Process form submission for each checked activity
        for act in checked_activities:
            act_name = act["activity"]
            chosen_list = request.form.getlist(f"choice_{act_name}")
            new_custom_tool = request.form.get(f"new_custom_{act_name}", "").strip()

            print(f"[DEBUG] Processing activity: {act_name}")
            print(f"  - Chosen tools: {chosen_list}")
            print(f"  - New custom tool: {new_custom_tool}")

            if "none" in chosen_list:
                act["status"] = "unimplemented"
                act["tools"].clear()
                act["custom"].clear()
                print(f"  -> Marked '{act_name}' as unimplemented.")
            elif chosen_list:
                final_tools = list(chosen_list)
                if new_custom_tool:
                    final_tools.append(new_custom_tool)
                    if new_custom_tool not in act["custom"]:
                        act["custom"].append(new_custom_tool)

                act["custom"] = [t for t in act["custom"] if t in final_tools]
                act["tools"] = [t for t in final_tools if t not in act["custom"]]
                act["status"] = "implemented"
                print(f"  -> Marked '{act_name}' as implemented with tools: {act['tools']}, custom: {act['custom']}")
            else:
                act["status"] = "unimplemented"
                act["tools"].clear()
                act["custom"].clear()
                print(f"  -> Marked '{act_name}' as unimplemented (empty selection).")

        # Save updates to file
        user_responses["activities"] = activities_list
        save_json(USER_RESPONSES_FILE, user_responses)

        # If any activities still have "checked" status, reload; otherwise, redirect to summary
        still_checked = [a for a in activities_list if a.get("status") == "checked"]
        if still_checked:
            print("[DEBUG] Still have 'checked' activities, reloading page.")
            return redirect(url_for("checking.verify_checked_activities"))
        else:
            print("[DEBUG] No more 'checked' activities, redirecting to summary.")
            return redirect(url_for("summary.display_summary"))

    # GET method: if no checked activities are left, redirect to summary.
    if not checked_activities:
        print("[DEBUG] No 'checked' activities. Redirecting to summary.")
        return redirect(url_for("summary.display_summary"))

    return render_template(
        "checking.html",
        activities=checked_activities,
        my_custom_tools=my_custom_tools,
        activity_relevant_tools=activity_relevant_tools
    )
