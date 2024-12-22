from data_loader import load_json
from tool_manager import get_tools_with_activities, display_tools_with_activities

if __name__ == "__main__":
    # Load JSON data
    file_path = "./data/dsomm.json"
    data = load_json(file_path)

    if not data:
        print("No data to process. Exiting.")
        exit()

    # Get tools and their associated activities
    tool_activities = get_tools_with_activities(data)

    # Display tools and their activities
    display_tools_with_activities(tool_activities)
