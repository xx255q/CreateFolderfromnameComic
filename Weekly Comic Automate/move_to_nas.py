import os
import shutil

source_folder = r"C:\Users\user\Documents\Comics\Done"
destination_folder = r"\\TOWER\Manga\Comics"

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

        shutil.rmtree(src_dir)
        print(f"Deleted original folder: {src_dir}")
