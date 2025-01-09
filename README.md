# **DevSecOps Pipeline Optimization**

This project focuses on step-by-step optimization of DevSecOps pipelines to enhance security, efficiency, and compliance by identifying and addressing gaps in tool usage and activity coverage.

## **Features**

1. **Tool Identification and Customization**:

   - Users can select tools for each pipeline stage.
   - An "Other" option allows manual entry of tools, which are temporarily stored for potential reuse.

2. **Activity Matching**:

   - Automatically maps tools to corresponding security activities.

3. **Gap Analysis**:

   - Identifies uncovered security activities and highlights areas requiring attention.

4. **Tool Suggestions**:

   - Recommends tools to address gaps, including descriptions and supported activities.
   - Questions about specific activity implementations within a selected tool group (e.g., "Do you want to implement GitLab SAST?" or "Would you like to enable Git Commit Signing?") occur **later in the workflow**, **after the initial tool selection** and activity matching phases.
   - Users can choose to implement suggested activities or explore alternative tools for the same activities.
   - This phased approach ensures users are not overwhelmed with decisions during the initial setup and fosters a guided, iterative process.

5. **Policy-Based Activities**:

   - Identifies activities requiring procedural or policy-based implementations.

6. **Comprehensive Reporting**:

   - Generates reports with the following options:
     - **Default Report**: Standard summary of findings.
     - **Full Report**: Exhaustive details on tools, activities, and gaps.
     - **Customized Report**: User-selected fields for tailored reporting.

7. **Iterative Development**:
   - Agile methodology for continuous refinement of the pipeline.

---

## **Workflow Steps**

1. **Initialization**:

   - Populate the system with initial data (`dsomm.json`, `pipeline_order.json`, `tools.json`).

2. **Tool Selection**:

   - Users select tools for each pipeline stage or manually input new tools.

3. **Activity Matching**:

   - Map selected tools to supported security activities.

4. **Gap Analysis**:

   - Compare implemented activities against recommended ones to identify gaps.

5. **Tool Suggestions and Activity Selection**:

   - After the **Gap Analysis**, users are prompted to select specific activities from within their chosen tools.
   - Example:
     - If the user selects **GitLab**, they will be asked later in the workflow whether they want to implement activities such as **GitLab SAST** or **Git Commit Signing**.
     - Alternative tools capable of performing the same activity (e.g., **Snyk** for SAST) will also be suggested.
   - This step ensures users have flexibility to tailor their pipeline while maintaining clarity and control.

6. **Final Report**:
   - Generate a structured report summarizing:
     - Tools and activities for each pipeline stage.
     - Policy-based activities.
     - Unimplemented tools and their descriptions.

---

### **Key Update for Tool Suggestions**

- **Activity-specific questions** are postponed until **after the initial tool selection** and activity matching phases.
- This approach avoids overwhelming users early in the process and ensures a logical flow aligned with the pipeline optimization steps.
