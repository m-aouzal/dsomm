import os
import json
from data_loader import load_json, save_json

def integrate_stages_into_questions(pipeline_file, questions_file, output_file):
    """
    Integrate pipeline stages into questions.json, aligning the questions file with the stages.
    """
    # Load pipeline_order.json
    if not os.path.exists(pipeline_file):
        print(f"Error: The file {pipeline_file} does not exist.")
        return

    pipeline_data = load_json(pipeline_file).get("pipeline", [])
    if not pipeline_data:
        print("Error: No data loaded from pipeline_order.json.")
        return

    # Load questions.json
    if not os.path.exists(questions_file):
        print(f"Error: The file {questions_file} does not exist.")
        return

    questions_data = load_json(questions_file)
    if not questions_data:
        print("Error: No data loaded from questions.json.")
        return

    # Align questions with pipeline stages
    updated_questions = []
    for stage in pipeline_data:
        stage_name = stage.get("stage", "")
        stage_questions = [
            q for q in questions_data
            if isinstance(q, dict) and q.get("stage") == stage_name
        ]

        # Append the aligned questions with the stage
        updated_questions.append({
            "stage": stage_name,
            "questions": stage_questions
        })

    # Save the updated questions.json
    save_json(updated_questions, output_file)
    print(f"Updated questions.json saved to {output_file}")

if __name__ == "__main__":
    # Define file paths
    pipeline_file = "../data/updated_pipeline_order.json"  # Path to pipeline_order.json
    questions_file = "../data/questions.json"  # Path to questions.json
    output_file = "../data/updated_questions.json"  # Output file for updated questions.json

    # Run integration
    integrate_stages_into_questions(pipeline_file, questions_file, output_file)
