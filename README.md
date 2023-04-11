# XXBagofScriptsforAutomation
There is now a number of scripts to hopefully help you from moving a first download folder of a weeks comics, convert them to a certain format, then moving to your last (main location) or for an existing library scripts to help filter:

Weekly Comic Automate scripts
1. use Windows to run run_all_scripts for example Weekly which will run the other three in order
2. move_weekly_to_converted - Moves all cbz and other comic files from all folders/subfolders to another location
3. convert_and_organize - Take a name like Spiderman Unbound 04 (2023)(Digital City) and creates a folder called Spiderman Unbound then moves the file into it
4. move_to_nas - Moves the now organized files to a network drive and should delete the original files

Scan and Scan2.0:

This Python script searches for similar folders within a root folder. 
It does this by iterating over all the directories within the root folder and comparing their names using the SequenceMatcher function from the difflib module. 
If the similarity between the names of two directories is greater than a specified threshold, then they are considered similar. 
The script then outputs a list of similar folder pairs to a text file

2.0:
second script prints the current folder it is checking before comparing it with other folders
(Shows real time what its doing)

MCV3.1:

The log function writes a message to a log file and also prints it to the console. The move_2000ad function moves all files in the source folder that start with the string '2000AD prog' to a destination folder. 
The first_scan function performs a first scan of the downloads folder, moving all files with a .cbr or .cbz extension to a converted folder. 
It creates a new subfolder with the main title of the comic if it doesn't exist. 
The second_scan function performs a second scan of the converted folder and moves all files with a .cbr or .cbz extension to a Done folder. 
Again, it creates a new subfolder with the main title of the comic if it doesn't exist. The remove_brackets function removes brackets from the end of folder names.

Overall, this script automates the process of organizing comic book files by moving them to specific folders and creating subfolders based on the main title of each comic. 
It also logs all actions taken by the script.

Takes the name of comic files and makes a folder with just the name then moves the comics over
Difference between MCV 3.0 and 3.1:

1. 2000AD specific rule to create folder (This needs to be before scans)
2. Rule to remove "("

6.2 Main Features:
Feature List:

File Extension Filtering: The script processes files with specific extensions: .cbr, .cbz, .pdf, and .epub.

Folder Title Extraction: The script extracts folder titles from file names by removing file extensions, contents inside square brackets and parentheses, unwanted characters, issue numbers, and years.

Folder Creation: If the destination folder does not exist, the script creates it automatically.

File Moving: The script moves comic files from the source folder to their corresponding destination folders, based on the extracted folder titles.

Error Handling and Retries: If an error occurs during file moving, the script retries up to 3 times, waiting 5 seconds between attempts.

Conflict Resolution: If a file with the same name already exists in the destination, the user can choose to overwrite, rename, or skip the file.

User Confirmation: After moving all files, the user is prompted to confirm if they want to keep the changes or revert them.

Reversing Changes: If the user decides to revert changes, the script moves the files back to their original locations and deletes any newly created folders.

Logging: The script logs all actions (including errors) with timestamps to a log file named 'comics_script.log'.

Filter_and_merge:

This script compares the similarity of different folders present in a specific directory and writes the similar folder pairs to a file. 
It then reads this file, groups the similar folders together, and displays the groups along with their folders to the user. 
The user selects the folders that they want to merge, and the script moves the files from the non-selected folders to the selected ones and deletes the non-selected folders. 
The user can change their selection and confirm their choice, or cancel the operation.

FM2.0:

This script is an improved version of the previous one Filter_and_merge. It has additional functionality that allows the user to create a new folder during the selection process and allows them to change their choices. 
It also has better error handling and code organization. Overall, it is more user-friendly and robust than the previous version.
