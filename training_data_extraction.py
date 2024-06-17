import json


def prepare_dataset(json_file, name, existing_dataset=[]):
    # Load the JSON data with the correct encoding
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    messages = data.get('messages', [])

    # Prepare the dataset
    dataset = []
    for i in range(len(messages) - 1):
        prev_msg = messages[i]
        next_msg = messages[i + 1]

        # Check if the next message is from the specified user
        if next_msg.get('from') == name:
            if next_msg.get('text') != '':
                dataset.append({
                    'previous_message': prev_msg.get('text', ''),
                    'next_message': next_msg.get('text', '')
                })

    # Add the new dataset to the existing dataset
    existing_dataset.extend(dataset)

    return existing_dataset


def save_dataset_to_file(dataset, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(dataset, file, ensure_ascii=False, indent=4)


# prepare data example
name = "Andrey Kupriyanov"
updated_dataset = []
file_names = ['onion_frenzy.json', 'innotyaga.json']
for file_name in file_names:
    updated_dataset = prepare_dataset(file_name, name, updated_dataset)
# Save the updated dataset to a file
output_file = 'updated_dataset.json'
save_dataset_to_file(updated_dataset, output_file)
