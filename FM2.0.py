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
        while True:
            chosen = input(f"Enter the number of the folder to keep in group {idx}, 0 to skip, 'n' to create a new folder: ")
            if chosen.isdigit():
                chosen = int(chosen)
                if 0 <= chosen <= len(similar_folders) + 1:
                    break
            elif chosen.lower() == 'n':
                new_folder_name = input("Enter the new folder name: ")
                break
            else:
                print("Invalid input. Please try again.")
                
        if chosen != 0:
            selections[idx] = (chosen, new_folder_name) if chosen.lower() == 'n' else chosen

    return selections

def merge_folders(selections, similar_folder_groups):
    for group, chosen in selections.items():
        group_folders = similar_folder_groups[group - 1]

        if isinstance(chosen, tuple):  # New folder case
            chosen_folder = chosen[1]
            merge_to = os.path.join(comic_root, chosen_folder)
            os.makedirs(merge_to, exist_ok=True)
        else:  # Existing folder case
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


def change_selection(similar_folder_groups, selections):
    while True:
        group_to_change = input("Enter the group number you want to change, or 'q' to quit: ")

        if group_to_change.isdigit():
            group_to_change = int(group_to_change)
            if group_to_change in selections:
                group_folders = similar_folder_groups[group_to_change - 1]
                print(f"\nGroup {group_to_change}:")
                for i, folder in enumerate(group_folders):
                    print(f"{i + 1}. {folder}")

                while True:
                    new_choice = input(f"Enter the number corresponding to the folder to keep in group {group_to_change}, 0 to skip, or 'n' to create a new folder: ")
                    if new_choice.isdigit():
                        new_choice = int(new_choice)
                        if 0 <= new_choice <= len(group_folders):
                            selections[group_to_change] = new_choice
                            break
                    elif new_choice.lower() == 'n':
                        new_folder_name = input("Enter the name of the new folder: ")
                        selections[group_to_change] = (new_choice.lower(), new_folder_name)
                        break
                    else:
                        print("Invalid input. Please try again.")
                break
            else:
                print("Invalid group number. Please try again.")
        elif group_to_change.lower() == 'q':
            break
        else:
            print("Invalid input. Please try again.")



def main():
    folder_pairs = get_folder_pairs()
    similar_folder_groups = find_similar_folders(folder_pairs)

    selections = {}
    for idx, group_folders in enumerate(similar_folder_groups):
        print(f"\nGroup {idx + 1}:")
        for i, folder in enumerate(group_folders):
            print(f"{i + 1}. {folder}")

        while True:
            choice = input(f"Enter the number corresponding to the folder to keep in group {idx + 1}, 0 to skip, 'n' to create a new folder, or 'm' to merge current selections: ")
            if choice.isdigit():
                chosen = int(choice)
                if 0 <= chosen <= len(group_folders):
                    selections[idx + 1] = chosen
                    break
            elif choice.lower() == 'm':
                break
            elif choice.lower() == 'n':
                new_folder_name = input("Enter the name of the new folder: ")
                selections[idx + 1] = (choice.lower(), new_folder_name)
                break
            else:
                print("Invalid input. Please try again.")

        if choice.lower() == 'm':
            break

    for _ in range(len(selections)):
        print("\nYour choices:")
        for group_idx, folder_idx in selections.items():
            if isinstance(folder_idx, tuple):  # Check if the user created a new folder
                print(f"Group {group_idx}: {folder_idx[1]} (New folder)")  # Use the new folder name
            else:
                print(f"Group {group_idx}: {similar_folder_groups[group_idx - 1][folder_idx - 1]}")

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

