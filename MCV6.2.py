import os
import re
import shutil
import datetime
import json
from pathlib import Path

CONFIG_FILE = f"{Path(__file__).stem}_config.json"

def get_folder_paths():
    last_saved = False
    source_folder = ""
    destination_folder = ""

    while not last_saved:
        use_last_saved = input("Use last saved paths? (y/n): ")
        if use_last_saved.lower() == 'y':
            try:
                config = load_config(CONFIG_FILE)
                source_folder = config["source_folder"]
                destination_folder = config["destination_folder"]
                last_saved = True
            except FileNotFoundError:
                print("No last saved paths found. Please enter new paths.")
        elif use_last_saved.lower() == 'n':
            source_folder = input("Enter source folder path: ")
            destination_folder = input("Enter destination folder path: ")
            if validate_paths(source_folder, destination_folder):
                confirm = input(f"Confirm new paths:\nSource: {source_folder}\nDestination: {destination_folder}\n(y/n): ")
                if confirm.lower() == 'y':
                    save_config(CONFIG_FILE, source_folder, destination_folder)
                    last_saved = True
                else:
                    print("Please re-enter paths.")
            else:
                print("Invalid paths. Please enter valid paths.")
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    return source_folder, destination_folder
    
def load_config(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def save_config(file_path, source_folder, destination_folder):
    config = {
        "source_folder": source_folder,
        "destination_folder": destination_folder
    }
    with open(file_path, 'w') as config_file:
        json.dump(config, config_file)

def main():
    source_folder, destination_folder = get_folder_paths()
    moved_files, created_folders = move_comics(source_folder, destination_folder)
    log(f"Moved {len(moved_files)} files and created {len(created_folders)} new folders.")

def validate_paths(source, destination):
    source_path = Path(source)
    destination_path = Path(destination)

    if source_path.exists() and source_path.is_dir() and destination_path.exists() and destination_path.is_dir():
        return True
    return False

def move_comics(source_folder, destination_folder):
    moved_files = []
    created_folders = []

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith(('.cbr', '.cbz', '.pdf', '.epub')):
                filepath = Path(root, file)
                folder_title = extract_folder_title(file)
                new_folder_path = Path(destination_folder, folder_title)

                if not new_folder_path.exists():
                    os.makedirs(new_folder_path)
                    log(f'Created new folder: {new_folder_path}')
                    created_folders.append(new_folder_path)

                new_file_path = new_folder_path / file
                move_file_with_retry(filepath, new_file_path, moved_files)

    return moved_files, created_folders

def move_file_with_retry(source, destination, moved_files):
    move_success = False
    retries = 3
    while not move_success and retries > 0:
        try:
            shutil.move(str(source), str(destination))
            log(f"Moved {source.name} to {destination}")
            moved_files.append((source, destination))
            move_success = True
        except shutil.Error as e:
            handle_shutil_error(e, source, destination)
            break
        except Exception as e:
            log(f"Error moving {source.name}: {str(e)}")
            if retries > 1:
                log(f"Retrying in 5 seconds... ({retries - 1} retries left)")
                time.sleep(5)
            retries -= 1
    if not move_success:
        log(f"Failed to move {source.name} after multiple attempts")

def handle_shutil_error(e, source, destination):
    if "already exists" in str(e):
        action = input(f"{source.name} already exists in destination. Overwrite (o), rename (r), or skip (s)? ")
        if action.lower() == 'o':
            os.remove(str(destination))
        elif action.lower() == 'r':
            new_file_name = input("Enter new file name: ")
            destination = destination.parent / new_file_name
            shutil.move(str(source), str(destination))
            log(f"Moved {source.name} to {destination} (renamed)")
        elif action.lower() == 's':
            return
    else:
        log(f"Error moving {source.name}: {str(e)}")

def log(message, level='info'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_levels = {'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
    logging.log(log_levels[level], f'{timestamp}: {message}')
    print(message)

def extract_folder_title(file):
    cleaned_title = Path(file).stem
    cleaned_title = re.sub(r'\[.*?\]|\(.*?\)', '', cleaned_title)
    cleaned_title = re.sub(r'[^\w\s\-\(\)]', '', cleaned_title)
    cleaned_title = re.sub(r'\d{1,3}(?=\s*\d{4})', '', cleaned_title)
    cleaned_title = re.sub(r'\d{4}', '', cleaned_title)
    cleaned_title = cleaned_title.strip()
    cleaned_title = re.sub(r'(\D|\sv\d+)\s+\d+', r'\1', cleaned_title)

    if "AD prog" in cleaned_title:
        cleaned_title = cleaned_title.replace("AD prog", "2000AD")

    return cleaned_title

if __name__ == "__main__":
    main()
