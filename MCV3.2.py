import os
import re
import shutil
import time
from unidecode import unidecode

LOG_FILE = 'move_comics.log'

def log(message):
    with open(LOG_FILE, 'a') as f:
        f.write(f'{message}\n')
    print(message)

def move_2000ad():
    source_folder = r"G:\Programs\Comics\Converted"
    destination_folder = r"G:\Programs\Comics\Done\2000AD"

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
    source_folder = r"G:\Programs\Comics\Converted"
    destination_folder = r"G:\Programs\Comics\Done"

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.cbr') or file.endswith('.cbz'):
                filepath = os.path.join(root, file)
                file_without_ext = os.path.splitext(file)[0]

                # Extract volume number from file name, if available
                v_number_match = re.search(r'v(\d+)', file_without_ext)
                v_number = None
                if v_number_match:
                    v_number = v_number_match.group(1)

                main_title = re.sub(r'\d+.*', '', file_without_ext).strip()
                cleaned_title = clean_title(main_title, v_number)

                if not cleaned_title:
                    cleaned_title = 'No Title'

                new_folder_path = os.path.join(destination_folder, cleaned_title)
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    log(f'Created new folder: {new_folder_path}')

                shutil.move(filepath, new_folder_path)
                log(f"Moved {file} to {new_folder_path}")





def clean_title(title, v_number=None):
    # Step 1 - Remove content inside brackets, unless it starts with 'v' followed by digits
    cleaned_title = re.sub(r'\[((?!v\d+).*?)\]', '', title)
    print(f"Step 1 - Remove content inside brackets, unless it starts with 'v' followed by digits: {cleaned_title}")

    # Step 2 - Remove content inside parentheses, unless it starts with 'v' followed by digits
    cleaned_title = re.sub(r'\(((?!v\d+).*?)\)', '', cleaned_title)
    print(f"Step 2 - Remove content inside parentheses, unless it starts with 'v' followed by digits: {cleaned_title}")

    # Step 3 - Remove unwanted characters (keep only alphanumeric, whitespace characters, hyphen, and parentheses)
    cleaned_title = re.sub(r'[^\w\s\-\(\)]', '', cleaned_title)
    print(f"Step 3 - Remove unwanted characters: {cleaned_title}")

    # Step 4 - Remove any leading or trailing whitespace
    cleaned_title = cleaned_title.strip()
    print(f"Step 4 - Remove leading and trailing whitespace: {cleaned_title}")

    # Step 5 - If there's a v_number available, add it after "v" if "v" is followed by a non-digit character or a space
    if v_number:
        cleaned_title = re.sub(r'(?<=v)(?=\D|$)', str(v_number), cleaned_title)
        print(f"Step 5 - Add the v_number after 'v' if 'v' is followed by a non-digit character or a space: {cleaned_title}")

    # Step 6 - Remove non-alphanumeric content inside parentheses
    cleaned_title = re.sub(r'\((\W+?)\)', '', cleaned_title)
    print(f"Step 6 - Remove non-alphanumeric content inside parentheses: {cleaned_title}")

    # Remove specific words: "Europe Comics", "Black Label", etc.
    cleaned_title = re.sub(r'Europe Comics|Black Label', '', cleaned_title)
    print(f"Remove specific words: {cleaned_title}")

    # Remove trailing parentheses, if any
    cleaned_title = re.sub(r'\($', '', cleaned_title)
    print(f"Remove trailing parentheses: {cleaned_title}")

    # Remove any leading or trailing whitespace after removing the trailing parentheses
    cleaned_title = cleaned_title.strip()
    print(f"Remove leading and trailing whitespace after removing trailing parentheses: {cleaned_title}")

    return cleaned_title


def clean_folders():
    root_folder = r"G:\Programs\Comics\Done"
    for root, dirs, files in os.walk(root_folder):
        for dir in dirs:
            cleaned_title = clean_title(dir)
            old_folder_path = os.path.join(root, dir)
            new_folder_path = os.path.join(root, cleaned_title)

            if old_folder_path != new_folder_path:
                os.rename(old_folder_path, new_folder_path)
                log(f"Renamed folder: {old_folder_path} to {new_folder_path}")


# Make sure you have the 'unidecode' package installed
# You can install it using: pip install unidecode

move_2000ad()
time.sleep(3)
first_scan()
clean_folders()
 
   
