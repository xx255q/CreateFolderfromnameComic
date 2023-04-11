import os
import re
import shutil

def main():
    source_folder = r"G:\Programs\Comics\Converted"
    destination_folder = r"G:\Programs\Comics\Done"

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.cbr') or file.endswith('.cbz'):
                filepath = os.path.join(root, file)
                folder_title = extract_folder_title(file)
                new_folder_path = os.path.join(destination_folder, folder_title)

                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    print(f'Created new folder: {new_folder_path}')

                shutil.move(filepath, new_folder_path)
                print(f"Moved {file} to {new_folder_path}")


def extract_folder_title(file):
    # Remove file extension
    cleaned_title = os.path.splitext(file)[0]

    # Remove content inside square brackets and parentheses
    cleaned_title = re.sub(r'\[.*?\]|\(.*?\)', '', cleaned_title)

    # Remove unwanted characters (keep only alphanumeric, whitespace characters, hyphen, and parentheses)
    cleaned_title = re.sub(r'[^\w\s\-\(\)]', '', cleaned_title)

    # Remove issue numbers followed by a space and a year (4 digits) or directly followed by parentheses
    cleaned_title = re.sub(r'(?<=\D)\d{1,3}(?=\s*\d{4}|\()', '', cleaned_title)

    # Remove the year itself
    cleaned_title = re.sub(r'\d{4}', '', cleaned_title)

    # Remove any trailing or leading spaces
    cleaned_title = cleaned_title.strip()

    # Remove trailing issue numbers
    cleaned_title = re.sub(r'\s+\d{1,3}$', '', cleaned_title)

    return cleaned_title



if __name__ == "__main__":
    main()
