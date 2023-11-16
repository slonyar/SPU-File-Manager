# this file is generated in QtDesign and is used as a template

import PyQt5


class UiMainWindow(object):
    def setup_ui(self, main_window):

        main_window.setObjectName("main_window")  # setting parameters for main window
        main_window.resize(640, 480)

        self.central_widget = PyQt5.QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")

        self.grid_layout = PyQt5.QtWidgets.QGridLayout(self.central_widget)  # creating layout
        self.grid_layout.setObjectName("grid_layout")

        self.tree_view = PyQt5.QtWidgets.QTreeView(self.central_widget)  # we are using tree view because we are making
        self.tree_view.setObjectName("tree_view")                        # file manager

        self.grid_layout.addWidget(self.tree_view, 0, 0, 1, 1)
        main_window.setCentralWidget(self.central_widget)

        self.menu_bar = PyQt5.QtWidgets.QMenuBar(main_window)  # creating menu bar in the top of window
        self.menu_bar.setGeometry(PyQt5.QtCore.QRect(0, 0, 640, 22))
        self.menu_bar.setObjectName("menu_bar")
        main_window.setMenuBar(self.menu_bar)

        self.status_bar = PyQt5.QtWidgets.QStatusBar(main_window)  # creating status bar
        self.status_bar.setObjectName("status_bar")
        main_window.setStatusBar(self.status_bar)

        self.retranslate_ui(main_window)
        PyQt5.QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        _translate = PyQt5.QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MainWindow"))
