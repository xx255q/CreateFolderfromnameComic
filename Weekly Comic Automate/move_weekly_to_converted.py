import os
import shutil

source_folder = r"Source_location"
destination_folder = r"Destination"

for root, _, files in os.walk(source_folder):
    for file in files:
        if file.endswith('.cbr') or file.endswith('.cbz'):
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_folder, file)
            shutil.move(source_file_path, destination_file_path)

print("All .cbr and .cbz files have been moved to the destination folder.")
