import os
import re
import shutil
import time

LOG_FILE = 'move_comics.log'

def log(message):
    with open(LOG_FILE, 'a') as f:
        f.write(f'{message}\n')
    print(message)

def move_2000ad():
    source_folder = r"C:\Users\user\Documents\Comics\Converted"
    destination_folder = r"C:\Users\user\Documents\Comics\Done\2000AD"

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.startswith('2000AD prog'):
                filepath = os.path.join(root, file)
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                    log(f'Created new folder: {destination_folder}')

                shutil.move(filepath, destination_folder)
                log(f"Moved {file} to {destination_folder}")

def first_scan():
    source_folder = r"C:\Users\user\Documents\Comics\Weekly"
    destination_folder = r"C:\Users\user\Documents\Comics\Converted"

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.cbr') or file.endswith('.cbz'):
                filepath = os.path.join(root, file)
                file_without_ext = os.path.splitext(file)[0]
                main_title = re.sub(r'\d+.*', '', file_without_ext).strip()

                new_folder_path = os.path.join(destination_folder, main_title)
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    log(f'Created new folder: {new_folder_path}')

                shutil.move(filepath, new_folder_path)
                log(f"Moved {file} to {new_folder_path}")

def second_scan():
    source_folder = r"C:\Users\user\Documents\Comics\Converted"
    destination_folder = r"C:\Users\user\Documents\Comics\Done"

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.cbr') or file.endswith('.cbz'):
                filepath = os.path.join(root, file)
                file_without_ext = os.path.splitext(file)[0]
                main_title = re.sub(r'\d+.*', '', file_without_ext).strip()

                new_folder_path = os.path.join(destination_folder, main_title)
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    log(f'Created new folder: {new_folder_path}')

                shutil.move(filepath, new_folder_path)
                log(f"Moved {file} to {new_folder_path}")

def remove_brackets():
    root_folder = r"C:\Users\user\Documents\Comics\Done"
    for root, dirs, files in os.walk(root_folder):
        for dir in dirs:
            if dir.endswith('('):
                old_folder_path = os.path.join(root, dir)
                new_folder_path = old_folder_path[:-1]
                os.rename(old_folder_path, new_folder_path)
                log(f"Renamed folder: {old_folder_path} to {new_folder_path}")

move_2000ad()
time.sleep(3)
first_scan()
second_scan()
remove_brackets()
