import os
import difflib
import shutil
from collections import defaultdict

comic_root = r"\\TOWER\Manga\Comics"
similarity_threshold = 0.85
input_file = "similar_folders.txt"

def get_folder_pairs():
    with open('similar_folders.txt', 'r', encoding='ISO-8859-1') as f:
        lines = [line.strip() for line in f.readlines()]

    folder_pairs = []
    for line in lines:
        if line.startswith('Skipping line:') or ' | ' not in line:
            continue
        folder1, folder2 = line.split(" | ")
        folder_pairs.append((folder1, folder2))

    return folder_pairs


def find_similar_folders(folder_pairs):
    similar_folder_groups = defaultdict(list)
    for folder1, folder2 in folder_pairs:
        if folder1 not in similar_folder_groups:
            similar_folder_groups[folder1] = [folder1]
        similar_folder_groups[folder1].append(folder2)
    return list(similar_folder_groups.values())



def display_and_select(similar_folder_groups):
    selections = {}

    for idx, (folder1, similar_folders) in enumerate(similar_folder_groups.items(), 1):
        print(f"\nGroup {idx}:")
        print(f"1. {folder1}")
        for i, folder in enumerate(similar_folders, 2):
            print(f"{i}. {folder}")
        chosen = int(input(f"Enter the number of the folder to keep in group {idx}, or 0 to skip: "))
        if chosen != 0:
            selections[idx] = chosen

    return selections


def merge_folders(selections, similar_folder_groups):
    for group, chosen in selections.items():
        group_folders = similar_folder_groups[group - 1]
        chosen_folder = group_folders[chosen - 1]
        merge_to = os.path.join(comic_root, chosen_folder)

        print(f"\nMerging folders in group {group} into '{chosen_folder}'...")

        folders_to_merge = [folder for folder in group_folders if folder != chosen_folder]

        for folder in folders_to_merge:
            folder_path = os.path.join(comic_root, folder)
            print(f"\nMerging folder '{folder}'...")
            for root, _, files in os.walk(folder_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(merge_to, file)
                    print(f"Moving file '{src_file}' to '{dst_file}'...")
                    shutil.move(src_file, dst_file)
            try:
                shutil.rmtree(folder_path)
                print(f"Merged and deleted folder {folder_path}")
            except FileNotFoundError as e:
                print(f"Error while deleting folder {folder_path}: {e}")



def main():
    folder_pairs = get_folder_pairs()
    similar_folder_groups = find_similar_folders(folder_pairs)

    selections = {}
    for idx, group_folders in enumerate(similar_folder_groups):
        print(f"\nGroup {idx + 1}:")
        for i, folder in enumerate(group_folders):
            print(f"{i + 1}. {folder}")

        while True:
            choice = input(f"Enter the number corresponding to the folder to keep in group {idx + 1}, 0 to skip, or 'm' to merge current selections: ")
            if choice.isdigit():
                chosen = int(choice)
                if 0 <= chosen <= len(group_folders):
                    break
            elif choice.lower() == 'm':
                break
            else:
                print("Invalid input. Please try again.")

        if choice.lower() == 'm':
            break
        elif chosen != 0:
            selections[idx + 1] = chosen  # Use idx + 1 instead of idx to match the printed group number

    for _ in range(len(similar_folder_groups)):
        print("\nYour choices:")
        for group_idx, folder_idx in selections.items():
            print(f"Group {group_idx}: {similar_folder_groups[group_idx - 1][folder_idx - 1]}")  # Use group_idx directly, as it's already 1-based

        decision = input("\nEnter 'c' to change a selection, 'y' to confirm, or 'n' to cancel: ").lower()
        if decision == 'c':
            change_selection(similar_folder_groups, selections)
        elif decision == 'y':
            break
        elif decision == 'n':
            print("Operation cancelled.")
            return
        else:
            print("Invalid input. Please try again.")

    merge_folders(selections, similar_folder_groups)









if __name__ == "__main__":
    main()
