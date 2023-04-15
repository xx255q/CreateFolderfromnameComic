import os
import shutil

source_folder = r"Source"
destination_folder = r"destination"

for root, _, files in os.walk(source_folder):
    for file in files:
        if file.endswith('.cbr') or file.endswith('.cbz') or file.endswith('.pdf'):
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_folder, file)
            shutil.move(source_file_path, destination_file_path)

    # Check if the folder is empty after moving files
    remaining_files = [f for f in os.listdir(root) if f.endswith('.cbr') or f.endswith('.cbz') or f.endswith('.pdf')]
    if not remaining_files:
        # Remove the empty folder
        try:
            os.rmdir(root)
            print(f"Deleted empty folder: {root}")
        except OSError as e:
            print(f"Error deleting folder {root}: {e}")

print("All .cbr, .cbz, and .pdf files have been moved to the destination folder.")
