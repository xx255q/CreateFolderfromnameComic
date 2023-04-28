import sys
import os
import io
import shutil
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QTreeView,
    QAbstractItemView,
    QPushButton,
    QSplitter,
    QFileSystemModel,
    QHeaderView,
    QMessageBox,
    QFileIconProvider
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDir, QModelIndex
from mcv_module import extract_folder_title, validate_paths, process_files, move_file_with_retry

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"




class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, line_numbers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_numbers = line_numbers or {}
        self.icon_provider = QFileIconProvider()

    def data(self, index, role):
        if role == Qt.DisplayRole and index.column() == 0:
            file_name = super().data(index, role)
            if self.isDir(index):
                return file_name
            else:
                # Line numbers will no longer be displayed in the destination preview
                return file_name
        elif role == Qt.DecorationRole and index.column() == 0:
            file_info = self.fileInfo(index)
            return self.icon_provider.icon(file_info)
        return super().data(index, role)



def generate_expected_folders(source_folder, destination_folder):
    expected_folders_list = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            folder_title = extract_folder_title(file)
            destination_path = os.path.join(destination_folder, folder_title)
            expected_folders_list.append(destination_path)
    return expected_folders_list

def create_virtual_folder_structure(destination_folder, expected_folders, expected_files):
    virtual_root = {
        'name': os.path.basename(destination_folder),
        'is_dir': True,
        'children': [],
        'parent': None
    }

    folder_dict = {destination_folder: virtual_root}

    for folder in expected_folders:
        file_name = os.path.basename(folder)
        folder_name = extract_folder_title(file_name)
        virtual_folder = {
            'name': folder_name,
            'is_dir': True,
            'children': [],
            'parent': virtual_root
        }
        virtual_root['children'].append(virtual_folder)
        folder_dict[folder] = virtual_folder

    for file in expected_files:
        file_name = os.path.basename(file)
        parent_folder = os.path.dirname(file)
        virtual_file = {
            'name': file_name,
            'is_dir': False,
            'parent': folder_dict[parent_folder]
        }
        folder_dict[parent_folder]['children'].append(virtual_file)

    return virtual_root



class VirtualFolderModel(QAbstractItemModel):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.icon_provider = QFileIconProvider()

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole and index.column() == 0:
            return node['name']
        elif role == Qt.DecorationRole and index.column() == 0:
            return self.icon_provider.icon(QFileIconProvider.Folder if node['is_dir'] else QFileIconProvider.File)

        return None

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.root)
        node = parent.internalPointer()
        if node['is_dir']:
            return len(node['children'])
        return 0

    def columnCount(self, parent):
        return 1

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self.root[row])

        node = parent.internalPointer()
        if node['is_dir']:
            return self.createIndex(row, column, node['children'][row])

        return QModelIndex()


    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        parent = node['parent']

        if parent is None:
            return QModelIndex()

        grandparent = parent['parent']
        if grandparent is None:
            row = -1
            for i, item in enumerate(self.root):
                if item == parent:
                    row = i
                    break
        else:
            row = grandparent['children'].index(parent)

        return self.createIndex(row, 0, parent)


class MainAppWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        screen = app.primaryScreen()
        screen_size = screen.size()
        self.setWindowTitle("MCV8.3")
        self.setGeometry(100, 100, int(screen_size.width() * 0.8), int(screen_size.height() * 0.8))

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        path_input_layout = QHBoxLayout()

        self.source_folder_label = QLabel("Source folder:")
        self.source_folder_input = QLineEdit()
        path_input_layout.addWidget(self.source_folder_label)
        path_input_layout.addWidget(self.source_folder_input)

        self.browse_source_button = QPushButton("Browse")
        self.browse_source_button.clicked.connect(self.browse_source_folder)
        path_input_layout.addWidget(self.browse_source_button)

        self.destination_folder_label = QLabel("Destination folder:")
        self.destination_folder_input = QLineEdit()
        path_input_layout.addWidget(self.destination_folder_label)
        path_input_layout.addWidget(self.destination_folder_input)

        self.browse_destination_button = QPushButton("Browse")
        self.browse_destination_button.clicked.connect(self.browse_destination_folder)
        path_input_layout.addWidget(self.browse_destination_button)

        layout.addLayout(path_input_layout)

        self.splitter = QSplitter()

        self.source_preview_tree = QTreeView()
        self.source_preview_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.destination_preview_tree = QTreeView()
        self.destination_preview_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.splitter.addWidget(self.source_preview_tree)
        self.splitter.addWidget(self.destination_preview_tree)

        layout.addWidget(self.splitter)

        buttons_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_processing)  # Connect the start_button to start_processing
        buttons_layout.addWidget(self.start_button)

        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo_last_move)  # Connect the undo_button to undo_last_move
        buttons_layout.addWidget(self.undo_button)
        self.move_history = []

        layout.addLayout(buttons_layout)
        self.move_history = []

    def get_source_line_numbers(self, source_folder):
        line_numbers = {}
        for i, filename in enumerate(os.listdir(source_folder), start=1):
            if os.path.isfile(os.path.join(source_folder, filename)):
                line_numbers[filename] = i
        return line_numbers
        
    def save_move_history_to_file(self, filename="move_history.txt"):
        with open(filename, "w") as file:
            for action in self.move_history:
                action_type = action["action"]

                if action_type == "move":
                    file.write(f'MOVED: {action["src"]} -> {action["dst"]}\n')
                elif action_type == "create":
                    file.write(f'CREATED: {action["path"]}\n')    

    def start_processing(self):
        source_folder = self.source_folder_input.text()
        destination_folder = self.destination_folder_input.text()

        if not validate_paths(source_folder, destination_folder):
            print("Invalid paths. Please enter valid paths.")
            return

        try:
            self.update_destination_preview(destination_folder)
            expected_folders = generate_expected_folders(source_folder, destination_folder)
            for folder in expected_folders:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    self.move_history.append({"action": "create", "path": folder})
                    with open("move_history.txt", "a") as f:
                        f.write(f"CREATED: {folder}\n")

            moved_files = process_files(source_folder, destination_folder)
            print(f"Moved files: {moved_files}")  # Debug print statement
            if moved_files:
                for src, dst in moved_files:
                    self.move_history.append({"action": "move", "src": src, "dst": dst})
                    with open("move_history.txt", "a") as f:
                        print(f"Writing to file: MOVED: {src} -> {dst}")  # Debug print statement
                        f.write(f"MOVED: {src} -> {dst}\n")

        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            print(traceback.format_exc())







            
    def move_back_files(self, src, dst):
        if os.path.isfile(dst):
            os.remove(dst)
        elif os.path.isdir(dst):
            if not os.listdir(dst):
                os.rmdir(dst)
            else:
                for item in os.listdir(dst):
                    src_item = os.path.join(src, item)
                    dst_item = os.path.join(dst, item)
                    self.move_back_files(src_item, dst_item)
                if not os.listdir(dst):
                    os.rmdir(dst)



    def undo_last_move(self):
        print("Undo function called")

        while self.move_history:
            last_action = self.move_history.pop()
            action_type = last_action["action"]
            print(f"Action type: {action_type}")

            if action_type == "move":
                src, dst = last_action["src"], last_action["dst"]
                print(f'Moving {dst} back to {src}')
                try:
                    move_file_with_retry(dst, src)
                except Exception as e:
                    print(f"Error moving the file: {e}")

            elif action_type == "create":
                folder = last_action["path"]
                try:
                    if not os.listdir(folder):  # Check if the folder is empty
                        print(f'Removing the folder: {folder}')
                        os.rmdir(folder)
                    else:
                        print(f'Error: The directory is not empty: {folder}')
                except Exception as e:
                    print(f"Error removing the folder: {e}")

        self.save_move_history_to_file()  # Add this line to save the move history to a text file




      



    def update_source_preview(self, source_folder):
        source_line_numbers = self.get_source_line_numbers(source_folder)
        source_model = CustomFileSystemModel(source_line_numbers)
        source_model.setRootPath(source_folder)
        source_model.setFilter(QDir.Files)
        self.source_preview_tree.setModel(source_model)
        self.source_preview_tree.setRootIndex(source_model.index(source_folder))
        self.source_preview_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def browse_source_folder(self):
        source_folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if source_folder:
            self.source_folder_input.setText(source_folder)
            self.update_source_preview(source_folder)
            destination_folder = self.destination_folder_input.text()
            if destination_folder:
                self.update_destination_preview(destination_folder)

    def browse_destination_folder(self):
        destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if destination_folder:
            self.destination_folder_input.setText(destination_folder)
            self.update_destination_preview(destination_folder)

    def update_destination_preview(self, destination_folder):
        source_folder = self.source_folder_input.text()
        print(f"Source folder: {source_folder}")
        print(f"Destination folder: {destination_folder}")

        source_line_numbers = self.get_source_line_numbers(source_folder)
        print(f"Source line numbers: {source_line_numbers}")

        # Generate the expected folder structure with files
        expected_folders = generate_expected_folders(source_folder, destination_folder)
        expected_files = []
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                folder_title = extract_folder_title(file)
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_folder, folder_title, file)
                expected_files.append(destination_path)

        # Create the virtual folder structure
        virtual_root = create_virtual_folder_structure(destination_folder, expected_folders, expected_files)  # Pass expected_files as an argument
        print(f"Virtual root: {virtual_root}")

        # Set the model for the destination preview tree
        destination_model = VirtualFolderModel(virtual_root['children'])
        self.destination_preview_tree.setModel(destination_model)
        self.destination_preview_tree.setItemsExpandable(True)
        self.destination_preview_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)








if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainAppWindow(app)
    main_window.show()

    sys.exit(app.exec_())
  