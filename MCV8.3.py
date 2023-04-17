import os
import re
import shutil
import json
import sys
import logging
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QTreeView, QAbstractItemView, QPushButton, QFileDialog, QSplitter, QFileSystemModel, QHeaderView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

logging.basicConfig(filename="mcv_log.txt", level=logging.INFO, format="%(message)s")

CONFIG_FILE = f"{Path(__file__).stem}_config.json"

class MainAppWindow(QMainWindow):
    def __init__(self, app, source_folder, destination_folder):
        super().__init__()

        # Assign source_folder and destination_folder to instance variables
        self.source_folder = source_folder
        self.destination_folder = destination_folder

        # Initialize move history
        self.move_history = []

        # Main window properties
        screen = app.primaryScreen()
        screen_size = screen.size()
        self.setWindowTitle('MCV8.0')
        self.setGeometry(100, 100, int(screen_size.width() * 0.8), int(screen_size.height() * 0.8))

        # Set up layout and central widget
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Source and destination folder input
        path_input_layout = QHBoxLayout()

        self.source_folder_label = QLabel("Source folder:")
        self.source_folder_input = QLineEdit()
        self.source_folder_input.textChanged.connect(self.update_preview)
        self.source_folder_input.textChanged.connect(self.update_destination_preview)
        self.source_folder_button = QPushButton("Browse")
        self.source_folder_button.clicked.connect(self.validate_and_select_source_folder)
        path_input_layout.addWidget(self.source_folder_label)
        path_input_layout.addWidget(self.source_folder_input)
        path_input_layout.addWidget(self.source_folder_button)

        self.destination_folder_label = QLabel("Destination folder:")
        self.destination_folder_input = QLineEdit()
        self.destination_folder_input.textChanged.connect(self.update_destination_preview)
        self.destination_folder_button = QPushButton("Browse")
        self.destination_folder_button.clicked.connect(self.validate_and_select_destination_folder)
        path_input_layout.addWidget(self.destination_folder_label)
        path_input_layout.addWidget(self.destination_folder_input)
        path_input_layout.addWidget(self.destination_folder_button)

        layout.addLayout(path_input_layout)

        # Preview tree
        self.splitter = QSplitter()

        self.source_preview_tree = QTreeView()
        self.source_preview_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.destination_preview_tree = QTreeView()
        self.destination_preview_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.splitter.addWidget(self.source_preview_tree)
        self.splitter.addWidget(self.destination_preview_tree)

        layout.addWidget(self.splitter, stretch=4)  # 80% of the space

        # Start and Undo buttons
        self.start_button = QPushButton("Start")
        self.start_button.setFixedWidth(self.start_button.width() // 2)
        self.start_button.clicked.connect(self.start_moving_comics)

        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo_move)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.undo_button)
        layout.addLayout(buttons_layout, stretch=1)  # 20% of the space

    def validate_and_select_source_folder(self):
        source_folder = QFileDialog.getExistingDirectory(None, "Select Source Folder")
        if source_folder:
            try:
                os.listdir(source_folder)
                self.source_folder_input.setText(source_folder)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot access the source folder: {e}")

    def validate_and_select_destination_folder(self):
        destination_folder = QFileDialog.getExistingDirectory(None, "Select Destination Folder")
        if destination_folder:
            try:
                os.listdir(destination_folder)
                self.destination_folder_input.setText(destination_folder)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot access the destination folder: {e}")

    def extract_folder_title(self, file):
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

    def start_moving_comics(self):
        source_folder = self.source_folder_input.text()
        destination_folder = self.destination_folder_input.text()

        if not validate_paths(source_folder, destination_folder):
            print("Invalid paths. Please enter valid paths.")
            return

        try:
            start_callback(self, source_folder, destination_folder)
        except Exception as e:
            logging.exception("An error occurred while moving comics.")
            print(f"An error occurred: {e}")

    def undo_move(self):
        if not self.last_move_history:
            QMessageBox.information(self, "Undo", "Nothing to undo.")
            return

        for last_move in reversed(self.last_move_history):
            try:
                shutil.move(last_move["dst"], last_move["src"])
                print(f"Moved {os.path.basename(last_move['dst'])} back to {os.path.dirname(last_move['src'])}")
            except Exception as e:
                logging.exception(f"An error occurred while undoing move: {last_move['dst']} to {last_move['src']}")
                print(f"An error occurred: {e}")
                QMessageBox.warning(self, "Error", f"Cannot undo the move: {e}")

            self.move_history.remove(last_move)

        self.last_move_history = []
        self.update_preview()
        self.update_destination_preview()


    def update_preview(self):
        # Set up file system model for preview tree
        file_model = QFileSystemModel()
        file_model.setRootPath(self.source_folder_input.text())
        self.source_preview_tree.setModel(file_model)
        self.source_preview_tree.setRootIndex(file_model.index(self.source_folder_input.text()))

        # Customize the preview tree here, e.g. hide columns, set column widths, etc.
        self.source_preview_tree.setColumnHidden(1, True)
        self.source_preview_tree.setColumnHidden(2, True)
        self.source_preview_tree.setColumnHidden(3, True)
        self.source_preview_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)


    def update_destination_preview(self):
        # Get the expected folder structure
        expected_folders = self.get_expected_folder_structure(self.source_folder_input.text(), self.destination_folder_input.text())

        # Create a temporary in-memory model for the destination preview tree
        temp_model = QStandardItemModel()
        temp_model.setHorizontalHeaderLabels(['Name'])

        # Set the model root item
        root_item = temp_model.invisibleRootItem()

        # Add the expected folders to the model
        for folder in expected_folders:
            folder_item = QStandardItem(os.path.basename(folder))
            folder_item.setEditable(False)
            root_item.appendRow(folder_item)

        # Set the model for the destination preview tree
        self.destination_preview_tree.setModel(temp_model)

        # Customize the preview tree here, e.g. hide columns, set column widths, etc.
        self.destination_preview_tree.setColumnHidden(1, True)
        self.destination_preview_tree.setColumnHidden(2, True)
        self.destination_preview_tree.setColumnHidden(3, True)
        self.destination_preview_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)

    def get_expected_folder_structure(self, source_folder, destination_folder):
        expected_folders = []

        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith(('.cbz', '.cbr')):
                    folder_title = self.extract_folder_title(file)
                    new_folder_path = os.path.join(destination_folder, folder_title)
                    expected_folders.append(new_folder_path)

        return expected_folders
        
def get_folder_paths():
    app = QApplication(sys.argv)
    source_folder = QFileDialog.getExistingDirectory(None, "Select Source Folder")
    destination_folder = QFileDialog.getExistingDirectory(None, "Select Destination Folder")

    if source_folder and destination_folder:
        if validate_paths(source_folder, destination_folder):
            confirm = input(f"Confirm new paths:\nSource: {source_folder}\nDestination: {destination_folder}\n(y/n): ")
            if confirm.lower() == 'y':
                save_config(CONFIG_FILE, source_folder, destination_folder)
            else:
                print("Please re-enter paths.")
        else:
            print("Invalid paths. Please enter valid paths.")
    else:
        print("Path selection canceled.")
        sys.exit()

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
                print(f"Failed to move file {src} to {dst} after {max_retries} attempts.")
                return False



def start_callback(main_app_instance, source_folder, destination_folder):
    main_app_instance.last_move_history = []
    expected_folders = main_app_instance.get_expected_folder_structure(source_folder, destination_folder)

    total_files = len(expected_folders)
    processed_files = 0

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.cbz', '.cbr')):
                folder_title = main_app_instance.extract_folder_title(file)
                new_folder_path = os.path.join(destination_folder, folder_title)

                try:
                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                except Exception as e:
                    logging.exception(f"An error occurred while creating folder: {new_folder_path}")
                    print(f"An error occurred: {e}")

                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(new_folder_path, file)

                move_file_with_retry(old_file_path, new_file_path)

                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f"Progress: {progress:.2f}%")

                move_info = {"src": old_file_path, "dst": new_file_path}
                main_app_instance.move_history.append(move_info)
                main_app_instance.last_move_history.append(move_info)




if __name__ == "__main__":
    if os.path.isfile(CONFIG_FILE):
        config = load_config(CONFIG_FILE)
        source_folder = config["source_folder"]
        destination_folder = config["destination_folder"]
    else:
        source_folder, destination_folder = get_folder_paths()

    app = QApplication(sys.argv)
    main_app = MainAppWindow(app, source_folder, destination_folder)
    main_app.show()
    sys.exit(app.exec_())
