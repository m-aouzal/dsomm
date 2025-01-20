from flask import Blueprint, render_template, request, redirect, url_for
import json
import os
from .utils import load_json, save_json, USER_RESPONSES_FILE

checking = Blueprint("checking", __name__)

DATA_FOLDER = "./data"

@checking.route("/", methods=["GET", "POST"])
def verify_checked_activities():
    """
    This route handles activities with 'status' == 'checked'.
    User can confirm (implemented), mark none (unimplemented), or select custom tools.
    """
    user_responses = load_json(USER_RESPONSES_FILE)
    activities_list = user_responses.get("activities", [])
    stage_tools = user_responses.get("tools", {})

    # 1. Gather 'checked' activities
    checked_activities = [act for act in activities_list if act.get("status") == "checked"]

    # 2. Collect all custom tools from user_responses to display under "My Tools"
    all_custom_tools = set()
    for stage, data in stage_tools.items():
        for c_tool in data.get("custom", []):
            all_custom_tools.add(c_tool)

    # Convert to sorted list for consistent display
    my_custom_tools = sorted(list(all_custom_tools))

    if request.method == "POST":
        form_data = dict(request.form)
        print("[DEBUG] POST data from checking_activities:", form_data)

        # Process each checked activity based on user choices
        for act in checked_activities:
            act_name = act["activity"]

            chosen_list = request.form.getlist(f"choice_{act_name}")
            new_custom_tool = request.form.get(f"new_custom_{act_name}", "").strip()

            print(f"[DEBUG] Processing activity: {act_name}")
            print(f"  - Chosen tools: {chosen_list}")
            print(f"  - New custom tool: {new_custom_tool}")

            # If user selected "none"
            if "none" in chosen_list:
                act["status"] = "unimplemented"
                act["tools"].clear()
                act["custom"].clear()
                print(f"  -> Marked '{act_name}' as unimplemented.")
            elif chosen_list:
                # Convert chosen tools to a list
                final_tools = list(chosen_list)

                # If user typed a new custom tool
                if new_custom_tool:
                    final_tools.append(new_custom_tool)
                    if new_custom_tool not in act["custom"]:
                        act["custom"].append(new_custom_tool)

                # Filter out any custom tools that aren't chosen now
                act["custom"] = [
                    t for t in act["custom"] if t in final_tools
                ]

                act["tools"] = [
                    t for t in final_tools if t not in act["custom"]
                ]

                act["status"] = "implemented"
                print(f"  -> Marked '{act_name}' as implemented with tools: {act['tools']}, custom: {act['custom']}")
            else:
                # No tools selected => unimplemented
                act["status"] = "unimplemented"
                act["tools"].clear()
                act["custom"].clear()
                print(f"  -> Marked '{act_name}' as unimplemented (empty selection).")

        # Save changes
        user_responses["activities"] = activities_list
        save_json(USER_RESPONSES_FILE, user_responses)

        # Check if there are still 'checked' activities after update
        still_checked = [a for a in activities_list if a.get("status") == "checked"]
        if still_checked:
            print("[DEBUG] Still have 'checked' activities, reloading page.")
            return redirect(url_for("checking.verify_checked_activities"))
        else:
            print("[DEBUG] No more 'checked' activities, redirecting to summary.")
            return redirect(url_for("summary.display_summary"))

    # GET method
    if not checked_activities:
        print("[DEBUG] No 'checked' activities. Redirecting to summary.")
        return redirect(url_for("summary.display_summary"))

    # Render template
    return render_template(
        "checking.html",
        activities=checked_activities,
        my_custom_tools=my_custom_tools
    )
