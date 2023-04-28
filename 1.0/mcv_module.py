import os
import re
import shutil
import json
import logging
import time
from pathlib import Path

logging.basicConfig(filename="mcv_log.txt", level=logging.INFO, format="%(message)s")

CONFIG_FILE = f"{Path(__file__).stem}_config.json"

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

def get_folder_paths(config):
    source_folder = config.get("source_folder", "")
    destination_folder = config.get("destination_folder", "")

    return source_folder, destination_folder


def load_config(file_path):
    try:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except Exception as e:
        logging.exception("An error occurred while loading the config file.")
        print(f"An error occurred: {e}")
        sys.exit()

def save_config(file_path, source_folder, destination_folder):
    config = {
        "source_folder": source_folder,
        "destination_folder": destination_folder
    }
    try:
        with open(file_path, 'w') as config_file:
            json.dump(config, config_file)
    except Exception as e:
        logging.exception("An error occurred while saving the config file.")
        print(f"An error occurred: {e}")

def validate_paths(source, destination):
    try:
        return os.path.isdir(source) and os.path.isdir(destination)
    except Exception as e:
        logging.exception("An error occurred while validating paths.")
        print(f"An error occurred: {e}")
        return False

def move_file_with_retry(src, dst, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            shutil.move(src, dst)
            print(f"Moved {os.path.basename(src)} to {os.path.dirname(dst)}")
            return True
        except Exception as e:
            logging.exception(f"An error occurred while moving file: {src} to {dst}. Attempt {attempt} of {max_retries}.")
            print(f"An error occurred: {e}")

            if attempt < max_retries:
                time.sleep(2 ** (attempt - 1))  # Exponential backoff
            else:
                print(f"Failed to move {os.path.basename(src)} after {max_retries} attempts. Skipping file.")
                return False


def process_files(source_folder, destination_folder):
    moved_files = []

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            folder_title = extract_folder_title(file)
            destination_path = os.path.join(destination_folder, folder_title)

            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

            dest_file_path = os.path.join(destination_path, file)
            if move_file_with_retry(file_path, dest_file_path):
                moved_files.append((file_path, dest_file_path))

    return moved_files



