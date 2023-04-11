import os
import re
import shutil
import datetime

def main():
    source_folder = r"G:\Programs\Comics\Converted"
    destination_folder = r"G:\Programs\Comics\Done"

    moved_files = []
    created_folders = []

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith(('.cbr', '.cbz', '.pdf', '.epub')):
                filepath = os.path.join(root, file)
                folder_title = extract_folder_title(file)
                new_folder_path = os.path.join(destination_folder, folder_title)

                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    log(f'Created new folder: {new_folder_path}')
                    created_folders.append(new_folder_path)

                new_file_path = os.path.join(new_folder_path, file)
                try:
                    shutil.move(filepath, new_file_path)
                    log(f"Moved {file} to {new_file_path}")
                    moved_files.append((filepath, new_file_path))
                except Exception as e:
                    log(f"Error moving {file}: {str(e)}")

    user_input = input("Keep the move? (y/n): ")
    if user_input.lower() == 'n':
        reverse_changes(moved_files, created_folders)

# ... (rest of the code remains the same)


def reverse_changes(moved_files, created_folders):
    for original_path, new_path in moved_files:
        try:
            shutil.move(new_path, original_path)
            log(f"Moved {os.path.basename(new_path)} back to {original_path}")
        except Exception as e:
            log(f"Error moving {os.path.basename(new_path)} back: {str(e)}")

    for folder in created_folders:
        try:
            os.rmdir(folder)
            log(f"Deleted folder: {folder}")
        except Exception as e:
            log(f"Error deleting folder {folder}: {str(e)}")

# ... (rest of the code remains the same)


def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('comics_script.log', 'a') as log_file:
        log_file.write(f'{timestamp}: {message}\n')
    print(message)

def extract_folder_title(file):
    # Remove file extension
    cleaned_title = os.path.splitext(file)[0]

    # Remove content inside square brackets and parentheses
    cleaned_title = re.sub(r'\[.*?\]|\(.*?\)', '', cleaned_title)

    # Remove unwanted characters (keep only alphanumeric, whitespace characters, hyphen, and parentheses)
    cleaned_title = re.sub(r'[^\w\s\-\(\)]', '', cleaned_title)

    # Remove issue numbers followed by a year (4 digits)
    cleaned_title = re.sub(r'\d{1,3}(?=\s*\d{4})', '', cleaned_title)

    # Remove the year itself
    cleaned_title = re.sub(r'\d{4}', '', cleaned_title)

    # Remove any trailing or leading spaces
    cleaned_title = cleaned_title.strip()

    # Remove issue numbers after volume number or any non-digit characters
    cleaned_title = re.sub(r'(\D|\sv\d+)\s+\d+', r'\1', cleaned_title)

    # Special case for "2000AD prog"
    if "AD prog" in cleaned_title:
        cleaned_title = cleaned_title.replace("AD prog", "2000AD")

    return cleaned_title

if __name__ == "__main__":
    main()
