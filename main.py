import os
import shutil
import subprocess
# from winshell import recycle_bin, undelete # only for windows
import sys
from os.path import expanduser, isdir, isfile

from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QCursor, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QMenu, QAction

from file_manager_main import UiMainWindow


class FileManager(UiMainWindow, QMainWindow):
    def __init__(self):
        super(FileManager, self).__init__()  # initializing
        self.setup_ui(self)
        self.setWindowTitle("SPU File Manager")
        self.file_system = QFileSystemModel()  # we must know what file_system on this computer
        self.default_show()  # setting default display settings
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)  # adding context menu
        self.tree_view.customContextMenuRequested.connect(self.context_menu)
        self.clipboard = ""  # creating clipboard to copying and cutting
        self.tree_view.doubleClicked.connect(self.double_click_open_file)  # now we can open files with double click
        self.cutting = False  # cut indicator
        self.home_directory = expanduser("~")  # finding home directory
        self.create_menu_panel()  # setting menu bar on top of window
        self.logs = list()  # now we keep logs in this list

    def default_show(self):  # show the list of root folder
        self.file_system.setRootPath(QDir.rootPath())  # default open folder is root
        self.tree_view.setModel(self.file_system)
        self.tree_view.setColumnWidth(0, 160)
        # self.tree_view.setRootIndex(self.file_system.index(self.home_directory))
        self.tree_view.setSortingEnabled(True)  # now we can sort by name, size, type and modification date

    def _set_logs(self, logs):  # we can add logs only inside the class (private method)

        if len(self.logs) == 10:  # we save only 10 last actions
            self.logs.pop(0)
            self.logs.append(logs)
        else:
            self.logs.append(logs)

    def cancel_action(self):  # method that undoes the last action
        self.statusBar().clearMessage()

        if len(self.logs) == 0:  # list of logs must be not empty
            self.statusBar().showMessage("You have not taken any action yet")
            return

        last_logs = self.logs[-1]

        if last_logs[0] == "delete":  # if last action was "delete"
            # for windows and linux we have 2 different ways of recovering files
            self.statusBar().showMessage("Sorry, but you can not restore deleted item")

            self.logs.pop()  # clear last log
            return

        elif last_logs[0] == "paste":  # if the last action was "paste"

            path = last_logs[1]  # path where the object was inserted
            if isdir(path):
                shutil.rmtree(path)  # if we inserted directory permanently delete it
            elif isfile(path):
                os.remove(path)  # same situation for file

            self.logs.pop()  # clear last log
            return

        elif last_logs[0] == "cut":  # if last action was "cut"

            destination_path = "/".join(last_logs[1].split("/")[0:-1])  # path where the object was before cutting
            source_path = last_logs[2]  # path were the object was inserted
            shutil.move(source_path, destination_path)  # move the object

            self.logs.pop()  # clear last log
            return

    def create_menu_panel(self):  # setting parameters for menu bar in top of window

        menu_file = QMenu("&File", self)  # adding menu with header "File"
        self.menu_bar.addMenu(menu_file)
        # adding actions for menu "File"
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        menu_file.addAction(quit_action)

        menu_edit = QMenu("&Edit", self)  # adding menu with header "Edit"
        self.menu_bar.addMenu(menu_edit)
        # adding actions for menu "Edit"
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.copy_file_or_directory)
        menu_edit.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(self.paste_file_or_directory)
        menu_edit.addAction(paste_action)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        cut_action.triggered.connect(self.cut_file_or_directory)
        menu_edit.addAction(cut_action)

        menu_edit.addSeparator()  # separating parts of menu "Edit"

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self.delete_file_or_directory)
        menu_edit.addAction(delete_action)

        menu_edit.addSeparator()  # separating parts of menu "Edit"

        cancel_action = QAction("Cancel", self)
        cancel_action.setShortcut(QKeySequence("Ctrl+Z"))  # making shortcut for canceling of the last action
        cancel_action.triggered.connect(self.cancel_action)
        menu_edit.addAction(cancel_action)

    def context_menu(self):  # making context menu
        c_menu = QMenu()
        cursor = QCursor()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)  # object to which the context menu is attached

        if isfile(path):  # if the object is file we can open it

            c_open = c_menu.addAction("Open")
            c_open.triggered.connect(self.open_file)

        c_copy = c_menu.addAction("Copy")
        c_paste = c_menu.addAction("Paste")
        c_cut = c_menu.addAction("Cut")
        c_menu.addSeparator()  # separate parts of context menu
        c_delete = c_menu.addAction("Delete")

        c_copy.triggered.connect(self.copy_file_or_directory)
        c_delete.triggered.connect(self.delete_file_or_directory)
        c_cut.triggered.connect(self.cut_file_or_directory)
        c_paste.triggered.connect(self.paste_file_or_directory)

        c_menu.exec_(cursor.pos())  # pass position of cursor to record clicks

    def open_file(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        file_path = self.file_system.filePath(current_index)  # path of the file we are working with

        if sys.platform == "win32":  # if operating system is windows we open file by the first way

            os.startfile(file_path)
            print(f"open file {file_path}")  # print log in the console

        else:  # on linux we do it by the second way

            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])
            print(f"open file {file_path}")  # print log in the console

    def double_click_open_file(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        file_path = self.file_system.filePath(current_index)  # path of the file we are working with

        if os.path.isfile(file_path):

            if sys.platform == "win32":  # if operating system is windows we open file by the first way

                os.startfile(file_path)
                print(f"open file {file_path}")  # printing log in the console

            else:  # on linux we do it by the second way

                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, file_path])
                print(f"open file {file_path}")  # printing log in the console

    def copy_file_or_directory(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)  # path of the object

        self.clipboard = path  # save path in clipboard
        self.cutting = False  # set cut indicator to False
        print(f"copy from {path}")  # printing logs

    def paste_file_or_directory(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)  # path of the object

        if isdir(self.clipboard):  # if we copied the directory

            if isdir(path):
                path = path + "/" + self.clipboard.split("/")[-1]  # if we paste to a directory

            elif isfile(path):
                path = "/".join(path.split("/")[0:-1]) + "/" + self.clipboard.split("/")[-1]  # if we paste to file

            try:
                shutil.copytree(self.clipboard, path)  # pasting directory to the path

                if self.cutting:  # instruction for cutting directory
                    self.delete_file_or_directory()
                    return

                logs = ("paste", path)
                print(f"paste to {logs[1]}")  # printing logs
                self._set_logs(logs)  # saving logs

            except FileExistsError:
                self.statusBar().showMessage(f"Copied folder already exists in this directory")
                # we display errors in status bar

        elif isfile(self.clipboard):  # if the copied object is file

            if isfile(path):
                path = "/".join(path.split("/")[0:-1])  # if we paste to file

            try:
                shutil.copy(self.clipboard, path)  # pasting file to the path

                if self.cutting:  # instruction for cutting file
                    self.delete_file_or_directory()
                    return

                logs = ("paste", path + "/" + self.clipboard.split("/")[-1])
                print(f"paste to {logs[1]}")  # printing logs
                self._set_logs(logs)  # saving logs

            except shutil.SameFileError:
                self.statusBar().showMessage(f"Copied file already exists in this directory")
                # display error in status bar

    def delete_file_or_directory(self):
        self.statusBar().clearMessage()

        if self.cutting:  # instruction for cutting object

            current_index = self.tree_view.currentIndex()
            path = self.file_system.filePath(current_index)  # path of the object into which we insert

            if isdir(self.clipboard):  # if the copied object is directory
                shutil.rmtree(self.clipboard)  # permanently remove directory from the previous path

                if isfile(path):  # if we pasted to file edit path for logs
                    path = "/".join(path.split("/")[0:-1])

                path = path + "/" + self.clipboard.split("/")[-1]
                logs = ("cut", self.clipboard, path)
                print(f"cut from {logs[1]} to {logs[2]}")  # printing logs
                self._set_logs(logs)  # saving logs

            elif isfile(self.clipboard):  # if the copied object is file
                os.remove(self.clipboard)  # permanently delete file from the previous directory

                if isfile(path):  # if we pasted to file edit path for logs
                    path = "/".join(path.split("/")[0:-1])

                logs = ("cut", self.clipboard, path + "/" + self.clipboard.split("/")[-1])
                print(f"cut from {logs[1]} to {logs[2]}")  # printing log
                self._set_logs(logs)  # saving log

            self.cutting = False  # set cut indicator to false
            return

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)  # path of the object

        if isdir(path):
            shutil.rmtree(path)  # permanently remove directory

            logs = ("delete", path)
            print(f"delete {logs[1]}")  # printing logs
            self._set_logs(logs)  # saving logs

        elif isfile(path):
            os.remove(path)  # permanently delete file

            logs = ("delete", path)
            print(f"delete {logs[1]}")  # printing log
            self._set_logs(logs)  # saving log

    def cut_file_or_directory(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)  # path of the object

        self.clipboard = path  # copy path to the clipboard
        self.cutting = True  # set cut indicator to True
        print(f"copy from {path}")  # printing logs


def launch_application():  # function for launch app

    application = QApplication(sys.argv)
    file_manager = FileManager()

    file_manager.show()  # show main window

    sys.exit(application.exec_())  # exit with exit-code


if __name__ == "__main__":
    launch_application()
