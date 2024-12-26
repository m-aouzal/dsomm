import json


def validate_pipeline_structure(pipeline_data):
    """Validate that the pipeline data is structured correctly."""
    if not isinstance(pipeline_data, dict) or "pipeline" not in pipeline_data:
        raise ValueError("The pipeline file should be a dictionary with a 'pipeline' key containing a list of stages.")

    if not isinstance(pipeline_data["pipeline"], list):
        raise ValueError("The 'pipeline' key should contain a list of stages.")

    for stage in pipeline_data["pipeline"]:
        if not isinstance(stage, dict) or "stage" not in stage or "tools" not in stage:
            raise ValueError("Each stage should be a dictionary with 'stage' and 'tools' keys.")
        if not isinstance(stage["tools"], list):
            raise ValueError(f"The tools for stage '{stage['stage']}' should be a list.")


def generate_questions(extracted_tools_file, pipeline_file, output_file):
    try:
        # Load extracted tools
        with open(extracted_tools_file, 'r') as f:
            extracted_tools = json.load(f)

        if not isinstance(extracted_tools, list):
            raise ValueError("The extracted tools file should contain a list of tools.")

        # Load updated pipeline order
        with open(pipeline_file, 'r') as f:
            pipeline_data = json.load(f)

        # Validate pipeline structure
        validate_pipeline_structure(pipeline_data)

        # Initialize questions structure
        questions = []

        # Process each stage in the pipeline
        for stage in pipeline_data["pipeline"]:
            stage_name = stage.get("stage", "Unnamed Stage")
            stage_questions = {
                "stage": stage_name,
                "questions": []
            }

            # General question for the stage
            stage_questions["questions"].append({
                "question_id": f"{stage_name.replace(' ', '_').lower()}_q1",
                "text": f"What are the key objectives for the '{stage_name}' stage?",
                "type": "text"
            })

            # Process tools associated with the stage
            tools = stage.get("tools", [])
            for tool in tools:
                tool_name = tool.get("Name", "Unnamed Tool")
                # Add a tool-specific question
                stage_questions["questions"].append({
                    "question_id": f"{stage_name.replace(' ', '_').lower()}_{tool_name.replace(' ', '_').lower()}",
                    "text": f"Do you use the tool '{tool_name}' in the '{stage_name}' stage?",
                    "type": "boolean"
                })

                # Optional: Add another tool-related question
                stage_questions["questions"].append({
                    "question_id": f"{stage_name.replace(' ', '_').lower()}_{tool_name.replace(' ', '_').lower()}_desc",
                    "text": f"How do you utilize the tool '{tool_name}' in your workflow?",
                    "type": "text"
                })

            # Append stage questions to the main list
            questions.append(stage_questions)

        # Save generated questions to the output file
        with open(output_file, 'w') as f:
            json.dump(questions, f, indent=4)
        print(f"Questions successfully generated and saved to {output_file}.")

    except Exception as e:
        print(f"Error occurred: {e}")


# File paths
extracted_tools_file = "../data/extracted_tools.json"
pipeline_file = "../data/updated_pipeline_order.json"
output_file = "../data/generated_questions.json"

# Generate questions
generate_questions(extracted_tools_file, pipeline_file, output_file)
