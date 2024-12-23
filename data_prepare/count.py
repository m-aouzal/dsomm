import json

# Function to count activities and unique activities (case-insensitive)
def count_activities_and_uniques(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)  # Load JSON data
        if isinstance(data, list):  # Check if data is a list
            # Create a tuple for each activity based on Dimension, Sub Dimension, and Activity (lowercase for comparison)
            activity_tuples = [
                (item['Dimension'].lower(), item['Sub Dimension'].lower(), item['Activity'].lower())
                for item in data
            ]
            total_activities = len(activity_tuples)  # Total activities
            unique_activities = len(set(activity_tuples))  # Unique activities
            return total_activities, unique_activities
        else:
            raise ValueError("The JSON structure is not a list.")

# File paths
file1_path = './data/evrything.json'  # File 1: everything
file2_path = './data/description_tools.json'  # File 2: description tools
file3_path = './preprocessed_data/unique_dsomm.json'  # File 3: unique_dsomm
file4_path = './data/total.json'  # File 4: total

# Calculate counts for each file
file1_total, file1_unique = count_activities_and_uniques(file1_path)
file2_total, file2_unique = count_activities_and_uniques(file2_path)
file3_total, file3_unique = count_activities_and_uniques(file3_path)
file4_total, file4_unique = count_activities_and_uniques(file4_path)

# Print the results
print(f"File 1 (everything.json) - Total Activities: {file1_total}, Unique Activities: {file1_unique}")
print(f"File 2 (description_tools.json) - Total Activities: {file2_total}, Unique Activities: {file2_unique}")
print(f"File 3 (unique_dsomm.json) - Total Activities: {file3_total}, Unique Activities: {file3_unique}")
print(f"File 4 (total.json) - Total Activities: {file4_total}, Unique Activities: {file4_unique}")
