import os
import shutil
import subprocess
import sys

from os.path import expanduser, isdir, isfile

from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QCursor, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QFileSystemModel, QMenu, QAction

from src.file_manager_main import UiMainWindow


class FileManager(UiMainWindow, QMainWindow):
    def __init__(self):
        super(FileManager, self).__init__()
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

    def default_show(self):
        self.file_system.setRootPath(QDir.rootPath())  # default open folder is root
        self.tree_view.setModel(self.file_system)
        self.tree_view.setColumnWidth(0, 160)
        self.tree_view.setSortingEnabled(True)

    def _set_logs(self, logs):

        if len(self.logs) == 10:  # we save only 10 last actions
            self.logs.pop(0)
            self.logs.append(logs)
        else:
            self.logs.append(logs)

    def cancel_action(self):  # method which undoes the last action
        self.statusBar().clearMessage()

        if len(self.logs) == 0:
            self.statusBar().showMessage("You have not taken any action yet")
            return

        last_logs = self.logs[-1]

        if last_logs[0] == "delete":

            self.statusBar().showMessage("Sorry, but you can not restore deleted item")

            self.logs.pop()
            return

        elif last_logs[0] == "paste":

            path = last_logs[1]
            if isdir(path):
                shutil.rmtree(path)
            elif isfile(path):
                os.remove(path)

            self.logs.pop()
            return

        elif last_logs[0] == "cut":

            destination_path = "/".join(last_logs[1].split("/")[0:-1])
            source_path = last_logs[2]
            shutil.move(source_path, destination_path)

            self.logs.pop()
            return

    def create_menu_panel(self):

        menu_file = QMenu("&File", self)
        self.menu_bar.addMenu(menu_file)

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        menu_file.addAction(quit_action)

        menu_edit = QMenu("&Edit", self)
        self.menu_bar.addMenu(menu_edit)

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

        menu_edit.addSeparator()

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self.delete_file_or_directory)
        menu_edit.addAction(delete_action)

        menu_edit.addSeparator()

        cancel_action = QAction("Cancel", self)
        cancel_action.setShortcut(QKeySequence("Ctrl+Z"))  # making shortcut for canceling of the last action
        cancel_action.triggered.connect(self.cancel_action)
        menu_edit.addAction(cancel_action)

    def context_menu(self):
        c_menu = QMenu()
        cursor = QCursor()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)  # object to which the context menu is attached

        if isfile(path):

            c_open = c_menu.addAction("Open")
            c_open.triggered.connect(self.open_file)

        c_copy = c_menu.addAction("Copy")
        c_paste = c_menu.addAction("Paste")
        c_cut = c_menu.addAction("Cut")
        c_menu.addSeparator()
        c_delete = c_menu.addAction("Delete")

        c_copy.triggered.connect(self.copy_file_or_directory)
        c_delete.triggered.connect(self.delete_file_or_directory)
        c_cut.triggered.connect(self.cut_file_or_directory)
        c_paste.triggered.connect(self.paste_file_or_directory)

        c_menu.exec_(cursor.pos())  # pass position of cursor to record clicks

    def open_file(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        file_path = self.file_system.filePath(current_index)

        if sys.platform == "win32":

            os.startfile(file_path)
            print(f"open file {file_path}")

        else:

            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])
            print(f"open file {file_path}")

    def double_click_open_file(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        file_path = self.file_system.filePath(current_index)  # path of the object we are working with

        if os.path.isfile(file_path):

            if sys.platform == "win32":

                os.startfile(file_path)
                print(f"open file {file_path}")

            else:

                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, file_path])
                print(f"open file {file_path}")

    def copy_file_or_directory(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)

        self.clipboard = path
        self.cutting = False
        print(f"copy from {path}")

    def paste_file_or_directory(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)

        if isdir(self.clipboard):

            if isdir(path):
                path = path + "/" + self.clipboard.split("/")[-1]

            elif isfile(path):
                path = "/".join(path.split("/")[0:-1]) + "/" + self.clipboard.split("/")[-1]

            try:
                shutil.copytree(self.clipboard, path)

                if self.cutting:
                    self.delete_file_or_directory()
                    return

                logs = ("paste", path)
                print(f"paste to {logs[1]}")
                self._set_logs(logs)

            except FileExistsError:
                self.statusBar().showMessage(f"Copied folder already exists in this directory")

        elif isfile(self.clipboard):

            if isfile(path):
                path = "/".join(path.split("/")[0:-1])

            try:
                shutil.copy(self.clipboard, path)

                if self.cutting:  # instruction for cutting file
                    self.delete_file_or_directory()
                    return

                logs = ("paste", path + "/" + self.clipboard.split("/")[-1])
                print(f"paste to {logs[1]}")
                self._set_logs(logs)

            except shutil.SameFileError:
                self.statusBar().showMessage(f"Copied file already exists in this directory")

    def delete_file_or_directory(self):
        self.statusBar().clearMessage()

        if self.cutting:  # instruction for cutting object

            current_index = self.tree_view.currentIndex()
            path = self.file_system.filePath(current_index)

            if isdir(self.clipboard):
                shutil.rmtree(self.clipboard)

                if isfile(path):
                    path = "/".join(path.split("/")[0:-1])

                path = path + "/" + self.clipboard.split("/")[-1]
                logs = ("cut", self.clipboard, path)
                print(f"cut from {logs[1]} to {logs[2]}")
                self._set_logs(logs)

            elif isfile(self.clipboard):
                os.remove(self.clipboard)

                if isfile(path):
                    path = "/".join(path.split("/")[0:-1])

                logs = ("cut", self.clipboard, path + "/" + self.clipboard.split("/")[-1])
                print(f"cut from {logs[1]} to {logs[2]}")
                self._set_logs(logs)

            self.cutting = False
            return

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)

        if isdir(path):
            shutil.rmtree(path)

            logs = ("delete", path)
            print(f"delete {logs[1]}")
            self._set_logs(logs)

        elif isfile(path):
            os.remove(path)

            logs = ("delete", path)
            print(f"delete {logs[1]}")
            self._set_logs(logs)

    def cut_file_or_directory(self):
        self.statusBar().clearMessage()

        current_index = self.tree_view.currentIndex()
        path = self.file_system.filePath(current_index)

        self.clipboard = path
        self.cutting = True
        print(f"copy from {path}")
