from src.training_data_extraction import process_telegram_data, process_zip_archive
import json


# Example usage
existing_dataset = []
json_filename = 'data/res.zip'
json_filename1 = 'data/res/result.json'
username = 'Egopoler'

# Process the data and update the dataset
#updated_dataset = process_telegram_data(json_filename1, existing_dataset, username)
updated_dataset = process_zip_archive(json_filename, existing_dataset, username)
print(updated_dataset[:5])

print("Aaaaaaaaaaaaaa")
# Save the updated dataset to a file
output_filename = 'datasets/Egopoler_dataset.json'
with open(output_filename, 'w', encoding='utf-8') as outfile:
    json.dump(updated_dataset, outfile, ensure_ascii=False, indent=4)

# Print the first 10 entries in the updated dataset
print(json.dumps(updated_dataset[:10], ensure_ascii=False, indent=4))
