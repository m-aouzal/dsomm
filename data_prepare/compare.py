import json

# Define the file paths
total_file_path = './data/total.json'  # Update this path
unique_dssom_file_path = './preprocessed_data/unique_dsomm.json'  # Update this path

# Load the JSON data from the files
with open(total_file_path, 'r') as total_file:
    total_data = json.load(total_file)

with open(unique_dssom_file_path, 'r') as unique_dssom_file:
    unique_dssom_data = json.load(unique_dssom_file)

# Create composite keys for both datasets
total_keys = {
    (
        entry["Dimension"].lower(),
        entry["Sub Dimension"].lower(),
        entry["Level"],
        entry["Activity"].lower(),
    )
    for entry in total_data
}
unique_dssom_keys = {
    (
        entry["Dimension"].lower(),
        entry["Sub Dimension"].lower(),
        entry["Level"],
        entry["Activity"].lower(),
    )
    for entry in unique_dssom_data
}

# Find activities that are in one file but not the other
in_total_not_in_unique = total_keys - unique_dssom_keys
in_unique_not_in_total = unique_dssom_keys - total_keys

# Prepare the results
results = {
    "In Total but not in Unique DSSOM": list(in_total_not_in_unique),
    "In Unique DSSOM but not in Total": list(in_unique_not_in_total),
}

# Display the results
print("Activities in Total but not in Unique DSSOM:")
for item in in_total_not_in_unique:
    print(item)

print("\nActivities in Unique DSSOM but not in Total:")
for item in in_unique_not_in_total:
    print(item)
