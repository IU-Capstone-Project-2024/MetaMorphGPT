from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os


def create_folder(drive, folder_name, parent_folder_id=None):
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        folder_metadata['parents'] = [{'id': parent_folder_id}]
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']


def upload_files(drive, dirpath, model_name, parent_folder_id=None):
    try:
        for item in os.listdir(dirpath):
            item_path = os.path.join(dirpath, item)
            if item != model_name and parent_folder_id is None:
                continue
            if os.path.isdir(item_path):
                # Create folder on Google Drive
                folder_id = create_folder(drive, item, parent_folder_id)
                # Recursively upload files in the folder
                upload_files(drive, item_path, model_name, folder_id)
            else:
                # Upload file to the specified folder
                file = drive.CreateFile({
                    'title': item,
                    'parents': [{'id': parent_folder_id}] if parent_folder_id else []
                })
                file.SetContentFile(item_path)
                file.Upload()
                print(f'Uploaded file: {item}')
        return 'Successfully uploaded files'
    except Exception as e:
        return f'Error uploading file: {e}'


# print(upload_files(drive,"./db_models", "andrey_model_4ep"))


def get_folder_id(drive, folder_name, parent_folder_id=None):
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]['id']
    else:
        return None


# Функция для загрузки файлов из папки на Google Диске в локальную папку
def download_files_from_folder(drive, folder_id, local_dir):
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    query = f"'{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    for file in file_list:
        file_path = os.path.join(local_dir, file['title'])
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            # Если это папка, то рекурсивно скачать её содержимое
            download_files_from_folder(drive, file['id'], file_path)
        else:
            # Скачивание файла
            file.GetContentFile(file_path)
            print(f"Downloaded file: {file_path}")

def authenticate():
    gauth = GoogleAuth()

    # Укажите путь к файлу с учетными данными
    credentials_file = "../credentials.json"

    # Проверьте, есть ли файл с учетными данными
    if os.path.exists(credentials_file):
        # Загрузите учетные данные из файла
        gauth.LoadCredentialsFile(credentials_file)
        if gauth.credentials is None:
            # Если учетные данные не валидны, выполните ручную авторизацию
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Если токен доступа истек, обновите его
            gauth.Refresh()
        else:
            # Если учетные данные валидны, авторизуйтесь
            gauth.Authorize()
    else:
        # Если файла с учетными данными нет, выполните ручную авторизацию
        gauth.LocalWebserverAuth()
        # Сохраните учетные данные в файл
        gauth.SaveCredentialsFile(credentials_file)

    drive = GoogleDrive(gauth)
    return drive

# model_name = "andrey_model_4ep"  # Имя модели, которую вы хотите скачать
# local_dir = "./newmodels"  # Локальная директория для загрузки

# # Получение ID папки модели
# model_folder_id = get_folder_id(drive, model_name)
# print(model_folder_id)

# if model_folder_id:
#     # Загрузка файлов из папки модели в локальную папку
#     download_files_from_folder(drive, model_folder_id, os.path.join(local_dir, model_name))
#     print(f"Model '{model_name}' downloaded successfully.")
# else:
#     print(f"Model folder '{model_name}' not found.")