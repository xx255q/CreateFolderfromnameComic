import os
import shutil
import datetime

source_folder = r"C:\Users\Jacob\Documents\Comics\Done"
destination_folder = r"\\TOWER\Manga\Comics"
log_folder = r"C:\Users\Jacob\Documents\Comics"

def log_moved_folders(moved_folders):
    log_file_name = f"moved_folders_log_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
    log_file_path = os.path.join(log_folder, log_file_name)
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for folder in moved_folders:
            log_file.write(f"{folder}\n")
        log_file.write("\n")

def main():
    moved_folders = []

    for root, dirs, files in os.walk(source_folder):
        for dir in dirs:
            src_dir = os.path.join(root, dir)
            dest_dir = os.path.join(destination_folder, dir)

            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print(f'Created new folder: {dest_dir}')

            for subdir, subdirs, subfiles in os.walk(src_dir):
                for file in subfiles:
                    src_file = os.path.join(subdir, file)
                    dest_file = os.path.join(dest_dir, file)
                    shutil.move(src_file, dest_file)
                    print(f"Moved {src_file} to {dest_file}")

            if set(os.listdir(src_dir)) == set(os.listdir(dest_dir)):
                shutil.rmtree(src_dir)
                print(f"Deleted original folder: {src_dir}")
                moved_folders.append(src_dir)
            else:
                print(f"Error: Failed to move {src_dir} to {dest_dir}")

    log_moved_folders(moved_folders)

if __name__ == "__main__":
    main()
