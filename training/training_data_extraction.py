import json
import re
import zipfile

def process_telegram_data(json_content, existing_dataset, username):
    def get_text(message):
        """Extract text from a message, handling cases where text is a list."""
        if isinstance(message['text'], list):
            return ' '.join(
                [part['text'] if isinstance(part, dict) and 'text' in part else part for part in message['text']])
        return message['text']

    def remove_links(text):
        """Remove URLs from the given text, case insensitive."""
        return re.sub(r'(?i)http\S+|www.\S+', '', text)

    #with open(json_filename, 'r', encoding='utf-8') as file:
    #    data = json.load(file)
    data = json.loads(json_content)
    # Determine if we are dealing with a single chat or multiple chats
    if 'chats' in data:
        chats = data['chats']['list']
    else:
        chats = [data]

    for chat in chats:
        # Get messages from the current chat
        messages = chat.get('messages', [])

        # Merge consecutive messages from the same sender
        merged_messages = []
        last_message = None

        for msg in messages:
            if 'text' not in msg or not msg['text']:
                continue
            msg_text = remove_links(get_text(msg))
            if last_message and last_message['from'] == msg['from']:
                last_message['text'] += " " + msg_text
            else:
                if last_message:
                    merged_messages.append(last_message)
                last_message = msg
                last_message['text'] = msg_text  # update the message text
        if last_message:
            merged_messages.append(last_message)

        # Create dataset
        for i in range(len(merged_messages) - 1):
            if merged_messages[i + 1]['from'] == username:
                previous_message = merged_messages[i]['text']
                next_message = merged_messages[i + 1]['text']
                # Skip messages longer than 2048 characters
                if len(previous_message) > 2048 or len(next_message) > 2048:
                    continue
                existing_dataset.append({
                    "previous_message": previous_message,
                    "next_message": next_message
                })

    return existing_dataset



def process_zip_archive(zip_filename, existing_dataset, username):
    with zipfile.ZipFile(zip_filename, 'r') as archive:
        for file_info in archive.filelist:
            #print(file_info.filename)
            if file_info.filename.endswith('.json') and file_info.filename.startswith(archive.filelist[0].filename):
                with archive.open(file_info.filename) as file:
                    print(file_info.filename)
                    json_content = file.read().decode('utf-8')
                    existing_dataset = process_telegram_data(json_content, existing_dataset, username)
    return existing_dataset