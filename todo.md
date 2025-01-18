


You are an expert software developer working on a Flask application for DevSecOps tool selection. You are implementing the Gap Analysis phase, which helps users address "unimplemented" activities one at a time.

**Existing Functionality:**

*   The application has already completed the initial tool selection and conflict resolution phases.
*   User selections and activity statuses are stored in `user_responses.json`.
*   A file named `gap.json` contains a list of activities prepared for Gap Analysis, including "unimplemented" activities.
*   Helper functions exist for:
    *   `load_configuration_data()`: Loads data from JSON files.
    *   `apply_standard_tool_selection()`: Applies standard tool selections to activities.
    *   `apply_custom_tool_selection()`: Applies custom tool selections (not used in this phase).
    *   `recalculate_activity_statuses()`: Recalculates activity statuses based on tool selections.
    *   `resolve_conflicts()`: Handles conflict resolution (already implemented).

**New Functionality: Gap Analysis (One Activity at a Time, Standard Tools Only, Batch Conflict Resolution, Automatic "unimplemented_confirmed")**

You need to implement the following within a new Blueprint named `gap_analysis`:

1.  **New Blueprint and Route:**
    *   Create a new Blueprint named `gap_analysis`.
    *   Create a new route `/gap-analysis/` within this Blueprint to handle GET and POST requests.

2.  **Gap Analysis Logic (within `/gap-analysis/`):**
    *   **GET Request:**
        *   Load `gap.json` to get the list of activities for Gap Analysis.
        *   Load `user_responses.json` to access user selections and activity statuses.
        *   Load `tool_activities.json` for tool details.
        *   Load `custom_tools.json` for managing custom tools.
        *   Find the first activity in `gap.json` with the status "unimplemented".
        *   If no "unimplemented" activity is found:
            *   Display a page (`checking.html`) that lists all activities with the status "checked".
            *   Allow the user to confirm these "checked" activities, changing their status to "implemented", or go back to change their selections.
            *   Upon confirmation, save the updated activities to `user_responses.json` and redirect to the summary page (`/summary/`).
        *   If an "unimplemented" activity is found:
            *   Display a form (`gap_analysis.html`) for the current activity.
            *   Display the activity name and description.
            *   Add a "See Full Details" button that shows more information from `level_activities.json` (details to be determined).
            *   Suggest standard tools from `tool_activities.json` that can implement the activity.
            *   Display a "My Tools" section with:
                *   Relevant standard tools previously selected by the user (from `user_responses.json`). Relevance could be based on:
                    *   Tools selected in the same stage as the current activity (if applicable).
                    *   Tools that can also perform the current activity (check `tool_activities.json`).
                *   Custom tools previously added by the user (from `custom_tools.json` and `user_responses.json`).
                    *   **Extraction of Custom Tools:** When loading `user_responses.json`, identify custom tools by comparing the tool names in `user_responses.json` against `tool_activities.json`. If a tool name (ignoring case) is not found in `tool_activities.json`, consider it a custom tool and add it to a list of custom tools.
                    *   **Store Custom Tools:** Maintain a separate list of custom tools, and save it to `custom_tools.json` whenever it's updated.
            *   Allow users to select multiple standard tools using checkboxes.
            *   **Important:** Do not display or apply custom tools in this step.
            *   Provide a "none" option to mark the activity as "unimplemented_confirmed" (no tool selected).

    *   **POST Request:**
        *   Process the user's choices for the current activity.
        *   **Apply Standard Tools:** If standard tools are selected, call **only** `apply_standard_tool_selection(activities_map, "Gap Analysis", tool_name, tool_activities_data)` for each selected tool.
            *   **Important:** Use `"Gap Analysis"` as the `stage` argument in `apply_standard_tool_selection()`. This allows you to potentially track tools selected during Gap Analysis differently and only the activities markes as unimplemented or checked should pass as the tool_activities_data.
        *   **"none" Option:** If "none" is selected, set the activity status to "unimplemented_confirmed", clear the `tools` list, and clear the `custom` list.
        *   **Update `activities_map`:** Update the activity's `status` and `tools` in the `activities_map` in memory (not in `gap.json` yet).
        
        *   **Important: Do not redirect to conflict resolution yet.**
        *   **Save to `user_responses.json`:** Save the updated `activities_map` to `user_responses.json`. Do not modify `gap.json` directly in this step.
        *   **Next Activity:** Redirect to `/gap-analysis/` to process the next "unimplemented" activity (GET request).

3.  **Conflict Resolution (After All Unimplemented Activities):**
    *   After the user has processed *all* "unimplemented" activities (or if there were no "unimplemented" activities to begin with), check for activities with "temporary" status in `activities_map`.
    *   If "temporary" activities exist:
        *   Redirect to `conflict_resolution.resolve_conflict` to resolve conflicts.
        *  this time if the user chooses not to implement a ceeratin activity it will be marked as unimplemented_confirmed 

**4. "Checked" Activity Confirmation:**
*   If no "unimplemented" or "temporary" activities remain, display a page (`checking.html`) that lists all activities with the status "checked".
*   Allow the user to confirm these "checked" activities, changing their status to "implemented", or go back to change their selections.
*   Upon confirmation, save the updated activities to `user_responses.json` and redirect to the summary page (`/summary/`).

**5. Automatically Mark as "unimplemented_confirmed":**
*   If an activity remains "unimplemented" after the user has gone through all activities in the Gap Analysis phase (meaning they did not select any tools for it), automatically mark its status as "unimplemented_confirmed".

**Specific Requirements:**

*   **Standard Tools Only in Gap Analysis:** Only standard tools should be applied during Gap Analysis using `apply_standard_tool_selection()`. Custom tool selection is handled separately or in previous phases.
*   **One Activity at a Time:** The user should be prompted to address one "unimplemented" activity at a time in the `/gap-analysis` route.
*   **Delayed Conflict Resolution:** Conflicts are resolved in a batch *after* the user has processed all "unimplemented" activities, not immediately after each selection.
*   **"My Tools" Section:** This section should dynamically display relevant standard tools and custom tools based on the user's previous selections.
*   **"unimplemented_confirmed" Status:** If the user does not select any tools for an activity during Gap Analysis (or if an activity remains "unimplemented" after conflict resolution), the activity's status should be set to "unimplemented_confirmed".
*   **Preserve "implemented" Status:** Activities marked as "implemented" before Gap Analysis should remain "implemented" throughout the process.
*   **"See Full Details" Functionality:** Display all details from the `level_activities.json` activity object, except for the `Tools` array, when the user requests it.
*   **Custom Tools Management:**
    *   Maintain a `custom_tools.json` file to store all custom tools added by the user.
    *   Identify custom tools by comparing tool names in `user_responses.json` against `tool_activities.json` (case-insensitive comparison).
    *   Add newly identified custom tools to `custom_tools.json`.

**Deliverables:**

*   The Python code for the `gap_analysis` Blueprint, including the route handler for `/gap-analysis/` (both GET and POST logic).
*   The HTML code for the `gap_analysis.html` template, including the "See Full Details" functionality and the "My Tools" section.
*   The HTML code for the `checking.html` template.
*   Any necessary modifications to existing helper functions to support the Gap Analysis phase.
and i any files is needed to keep the application modular 
