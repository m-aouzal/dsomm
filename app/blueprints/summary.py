from flask import Blueprint, render_template, request, redirect, url_for
import json
import os
from .utils import load_json, save_json, USER_RESPONSES_FILE

summary = Blueprint("summary", __name__)

DATA_FOLDER = "./data"
DSOMM_FILE = os.path.join(DATA_FOLDER, "dsomm.json")

@summary.route("/")
def display_summary():
    """
    Displays the synthesis dashboard report.
    It shows:
      - Chosen security level,
      - Selected stages,
      - Activities (grouped in the following order:
           Implemented, Policies, Not Implemented)
      - For implemented activities, shows both standard and custom tools.
      - For policies, no tools are displayed.
    """
    user_responses = load_json(USER_RESPONSES_FILE)
    selected_level = user_responses.get("selected_level", "N/A")
    stages = user_responses.get("stages", [])
    tools_by_stage = user_responses.get("tools", {})
    all_activities = user_responses.get("activities", [])

    # Group activities:
    implemented = [act for act in all_activities if act.get("status") == "implemented"]
    policies = [act for act in all_activities if act.get("status") == "policy"]
    not_implemented = [act for act in all_activities if act.get("status") not in ["implemented", "policy"]]

    return render_template("summary.html",
                           selected_level=selected_level,
                           stages=stages,
                           tools_by_stage=tools_by_stage,
                           implemented=implemented,
                           policies=policies,
                           not_implemented=not_implemented)

@summary.route("/complete", methods=["GET", "POST"])
def complete_report():
    """
    Displays a complete report.
    By default, the report shows the following fields:
      - Dimension, Sub Dimension, Activity, Description.
    The user may select additional fields from:
      Level, Risk, Measure, Knowledge, Resources, Time, Usefulness, SAMM, ISO 27001:2017, ISO 27001:2022.
    The complete report is rendered as a dashboard using Bootstrap cards.
    """
    dsomm_data = load_json(DSOMM_FILE)

    # Default fields for the complete report
    default_fields = ["Dimension", "Sub Dimension", "Activity", "Description"]
    # Additional fields that the user can optionally include.
    additional_fields_available = ["Level", "Risk", "Measure", "Knowledge", "Resources", "Time", "Usefulness", "SAMM", "ISO 27001:2017", "ISO 27001:2022"]

    if request.method == "POST":
        user_selected_fields = request.form.getlist("fields")
        # Combine default and user-selected additional fields.
        complete_fields = default_fields + user_selected_fields
    else:
        complete_fields = default_fields

    return render_template("complete_report.html",
                           dsomm_data=dsomm_data,
                           complete_fields=complete_fields,
                           additional_fields_available=additional_fields_available)
