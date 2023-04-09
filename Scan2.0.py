import os
import difflib

def get_similar_folders(root_folder, similarity_threshold=0.9):
    folder_names = [folder for folder in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, folder))]
    similar_folder_pairs = []

    print("Comparing folders...")

    for i, folder1 in enumerate(folder_names):
        print(f"Checking folder '{folder1}'")
        for folder2 in folder_names[i+1:]:
            similarity = difflib.SequenceMatcher(None, folder1, folder2).ratio()
            if similarity > similarity_threshold:
                print(f"Found similar folders: {folder1} | {folder2}")
                similar_folder_pairs.append((folder1, folder2))
        print(f"Finished checking folder '{folder1}'")

    return similar_folder_pairs

def write_similar_folders_to_file(similar_folder_pairs, output_file="similar_folders.txt"):
    print(f"Writing similar folder pairs to '{output_file}'...")
    
    with open(output_file, "w") as file:
        if similar_folder_pairs:
            file.write("Similar folders found:\n")
            for folder1, folder2 in similar_folder_pairs:
                file.write(f"{folder1} | {folder2}\n")
        else:
            file.write("No similar folders found.\n")

    print("Writing complete.")


root_folder = r"\\TOWER\Manga\Comics"
print(f"Starting search for similar folders in '{root_folder}'")
similar_folder_pairs = get_similar_folders(root_folder)
write_similar_folders_to_file(similar_folder_pairs)
