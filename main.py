from training_data_extraction import process_telegram_data
import json


# Example usage
existing_dataset = []
json_filename = 'innotyaga.json'
username = 'Andrey Kupriyanov'

# Process the data and update the dataset
updated_dataset = process_telegram_data(json_filename, existing_dataset, username)

# Save the updated dataset to a file
output_filename = 'dataset.json'
with open(output_filename, 'w', encoding='utf-8') as outfile:
    json.dump(updated_dataset, outfile, ensure_ascii=False, indent=4)

# Print the first 10 entries in the updated dataset
print(json.dumps(updated_dataset[:10], ensure_ascii=False, indent=4))
