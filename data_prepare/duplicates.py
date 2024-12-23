import json
from collections import Counter

# Function to count activities and find duplicates
def find_duplicates(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        if isinstance(data, list):
            # Create a tuple for each activity based on Dimension, Sub Dimension, and Activity
            activity_tuples = [
                (item['Dimension'], item['Sub Dimension'], item['Activity'])
                for item in data
            ]
            # Count occurrences of each activity tuple
            counts = Counter(activity_tuples)
            # Find duplicates (activities with count > 1)
            duplicates = [activity for activity, count in counts.items() if count > 1]
            return duplicates
        else:
            raise ValueError("The JSON structure is not a list.")

# File path
file3_path = './data/total.json'  # File 3: combined

# Find duplicates
duplicates = find_duplicates(file3_path)

# Print 10 examples of duplicates
print("Duplicate examples (up to 10):")
for example in duplicates[:10]:
    print(example)
