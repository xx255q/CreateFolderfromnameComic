import os
import subprocess

scripts_folder = r"C:\Users\user\Documents\Scripts\Weekly Comic Automate"

# Define the order of the scripts
script_order = [
    "move_weekly_to_converted.py",
    "convert_and_organize.py",
    "move_to_nas.py",
]

# Run the scripts in the defined order
for script in script_order:
    script_path = os.path.join(scripts_folder, script)
    print(f"Running {script_path}...")
    subprocess.run(["python", script_path])
    print(f"{script_path} completed.")
