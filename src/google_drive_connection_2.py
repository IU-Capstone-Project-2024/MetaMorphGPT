from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io

# Укажите путь к файлу с ключом сервисного аккаунта
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Замените на реальный путь к файлу JSON

# Укажите области доступа
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def get_folder_id(service, folder_name, parent_folder_id=None):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    try:
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']
        else:
            return None
    except Exception as e:
        print(f"Error searching for folder '{folder_name}': {e}")
        return None

def create_folder(service, folder_name, parent_folder_id=None):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_files(service, dirpath, model_name, parent_folder_id, Is_Root=False):
    try:
        for item in os.listdir(dirpath):
            item_path = os.path.join(dirpath, item)
            if item != model_name and Is_Root:
                continue
            if os.path.isdir(item_path):
                # Create folder on Google Drive
                folder_id = create_folder(service, item, parent_folder_id)
                # Recursively upload files in the folder
                upload_files(service, item_path, model_name, folder_id)
            else:
                # Upload file to the specified folder
                file_metadata = {
                    'name': item,
                    'parents': [parent_folder_id]
                }
                media = MediaFileUpload(item_path)
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f'Uploaded file: {item}')
        return 'Successfully uploaded files'
    except Exception as e:
        return f'Error uploading file: {e}'

def download_files_from_folder(service, folder_id, local_dir):
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    query = f"'{folder_id}' in parents and trashed=false"
    try:
        results = service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)').execute()
        items = results.get('files', [])
        
        for item in items:
            file_path = os.path.join(local_dir, item['name'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # Если это папка, то рекурсивно скачать её содержимое
                download_files_from_folder(service, item['id'], file_path)
            else:
                # Скачивание файла
                request = service.files().get_media(fileId=item['id'])
                fh = io.FileIO(file_path, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                print(f"Downloaded file: {file_path}")
    except Exception as e:
        print(f"Error downloading files from folder '{folder_id}': {e}")

def try_get_model(service, models_folder_id, model_name):
    local_model_dir = os.path.join("models", model_name)
    
    # Проверка, существует ли модель локально
    if not os.path.exists(local_model_dir):
        print(f"Model '{model_name}' not found locally. Downloading from Google Drive...")
        
        # Получение ID папки модели на Google Диске
        model_folder_id = get_folder_id(service, model_name, models_folder_id)
        
        if model_folder_id:
            # Загрузка файлов из папки модели в локальную папку
            download_files_from_folder(service, model_folder_id, local_model_dir)
            print(f"Model '{model_name}' downloaded successfully.")
        else:
            print(f"Model folder '{model_name}' not found on Google Drive.")
    else:
        print(f"Model '{model_name}' found locally. No need to download.")

# if __name__ == "__main__":
#     drive_service = get_drive_service()
#     models_folder_name = "models"  # Имя папки для моделей на Google Диске
#     models_folder_id = get_folder_id(drive_service, models_folder_name)

#     if not models_folder_id:
#         print(f"Models folder '{models_folder_name}' not found on Google Drive.")
#     else:
#         model_name = "0002"  # Имя модели, которую вы хотите скачать
#         local_dir = "./models"  # Локальная директория для загрузки

#         # Пример загрузки модели
#         try_get_model(drive_service, models_folder_id, model_name)
#         #upload_files(drive_service, "./models", "0002", models_folder_id, True)
