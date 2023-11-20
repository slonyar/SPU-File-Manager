import sys

from PyQt5.QtWidgets import QApplication
from src.file_manager_class import FileManager


def launch_application():  # function for launch app

    application = QApplication(sys.argv)
    file_manager = FileManager()

    file_manager.show()

    sys.exit(application.exec_())


if __name__ == "__main__":
    launch_application()
