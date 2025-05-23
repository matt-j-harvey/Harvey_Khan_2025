import numpy as np
import pyqtgraph
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from tqdm import tqdm

import tables
import sys

import MVAR_Utils_2P


class lick_threshold_window(QWidget):

    def __init__(self, session_list, parent=None):
        super(lick_threshold_window, self).__init__(parent)

        # Setup Window
        self.setWindowTitle("Set Lick Thresholds")
        self.setGeometry(0, 0, 1500, 500)

        # Create Variable Holders
        self.session_list = session_list
        self.channel_dictionary = MVAR_Utils_2P.load_rig_1_channel_dict()
        self.default_lick_threshold = 500
        self.current_lick_threshold = 500
        self.current_session_index = 0
        self.current_lick_trace = None

        # Create Widgets

        # Current Session Label
        self.session_label = QLabel("Session: " + str(session_list[self.current_session_index]))

        # Lick Threshold Display Widget
        self.lick_display_view_widget = QWidget()
        self.lick_display_view_widget_layout = QGridLayout()
        self.lick_display_view = pyqtgraph.PlotWidget()
        self.lick_display_view_widget_layout.addWidget(self.lick_display_view, 0, 0)
        self.lick_display_view_widget.setLayout(self.lick_display_view_widget_layout)
        self.lick_display_view_widget.setMinimumWidth(1000)

        # Session List Widget
        self.session_list_widget = QListWidget()
        self.session_list_widget.setCurrentRow(0)
        self.session_list_widget.setFixedWidth(250)
        self.session_list_widget.currentRowChanged.connect(self.set_session)

        self.lick_trace_list = []
        self.lick_threshold_list = []
        self.threshold_status_list = []

        # load Data
        self.load_all_data()

        # Lick Threshold Spinner
        self.lick_threshold_spinner = QDoubleSpinBox()
        self.lick_threshold_spinner.setValue(self.current_lick_threshold)
        self.lick_threshold_spinner.setMinimum(0)
        self.lick_threshold_spinner.setMaximum(10000)
        self.lick_threshold_spinner.valueChanged.connect(self.change_lick_threshold)
        self.lick_threshold_spinner.setSingleStep(100)

        # Set Lick Threshold Button
        self.set_lick_threshold_button = QPushButton("Set Lick Threshold")
        self.set_lick_threshold_button.clicked.connect(self.set_lick_threshold)

        # Create Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Add Transformation Widgets
        self.layout.addWidget(self.session_label,                   0, 0, 1, 3)

        self.layout.addWidget(self.lick_display_view_widget,        1, 0, 1, 2)
        self.layout.addWidget(self.set_lick_threshold_button,       2, 0, 1, 1)
        self.layout.addWidget(self.lick_threshold_spinner,          2, 1, 1, 1)

        self.layout.addWidget(self.session_list_widget,             1, 2, 2, 1)


        # Plot First Item
        self.lick_threshold_line = pyqtgraph.InfiniteLine()
        self.lick_threshold_line.setAngle(0)
        self.lick_threshold_line.setValue(self.current_lick_threshold)
        self.lick_trace_curve = pyqtgraph.PlotCurveItem()
        self.lick_display_view.addItem(self.lick_threshold_line)
        self.lick_display_view.addItem(self.lick_trace_curve)


        self.show()

    def load_all_data(self):

        print("Loading Lick Data, Please Wait: ")

        # Iterate Through All Sessions
        number_of_sessions = len(self.session_list)
        print("number_of_sessions", number_of_sessions)
        for session_index in tqdm(range(number_of_sessions)):

            # Get Current Session
            current_session = self.session_list[session_index]

            # Get Session Name
            session_name = current_session.split('/')[-1]
            self.session_list_widget.addItem(session_name)

            # Load Lick Trace
            ai_data = np.load(os.path.join(current_session, "Behaviour", "Downsampled_AI_Matrix_Framewise.npy"))
            print("ai_data", np.shape(ai_data))
            lick_trace = ai_data[self.channel_dictionary["Lick"]]
            self.lick_trace_list.append(lick_trace)

            # See If We Already Have a Lick Threshold Set
            if os.path.exists(os.path.join(current_session, "Behaviour", "Lick_Threshold.npy")):
                lick_threshold = np.load(os.path.join(current_session,  "Behaviour", "Lick_Threshold.npy"))
                self.lick_threshold_list.append(lick_threshold)
                self.threshold_status_list.append(1)
                already_set = True
            else:
                self.lick_threshold_list.append(self.default_lick_threshold)
                self.threshold_status_list.append(0)
                already_set = False

            # Update List Widget
            if already_set == True:
                self.session_list_widget.item(session_index).setBackground(QColor("#00c957"))
            else:
                self.session_list_widget.item(session_index).setBackground(QColor("#fc0303"))


    def change_lick_threshold(self):
        self.current_lick_threshold = self.lick_threshold_spinner.value()
        self.lick_threshold_line.setValue(self.current_lick_threshold)

    def set_lick_threshold(self):

         # Get Output Path
        file_save_directory = os.path.join(self.session_list[self.current_session_index], "Behaviour", "Lick_Threshold.npy")

        # Save File
        np.save(file_save_directory, self.current_lick_threshold)

        self.lick_threshold_list[self.current_session_index] = 1
        self.session_list_widget.item(self.current_session_index).setBackground(QColor("#00c957"))


    def set_session(self):

        self.current_session_index = int(self.session_list_widget.currentRow())
        print("current session index")

        # Plot Lick Trace
        self.lick_trace_curve.setData(self.lick_trace_list[self.current_session_index])

        # Set Current Threshold
        self.current_lick_threshold = self.lick_threshold_list[self.current_session_index]
        self.lick_threshold_spinner.setValue(self.current_lick_threshold)
        self.lick_threshold_line.setValue(self.current_lick_threshold)




def set_lick_thresholds(session_list):

    app = QApplication(sys.argv)

    window = lick_threshold_window(session_list)
    window.show()

    app.exec_()



data_root = r"C:\Users\matth\OneDrive - The Francis Crick Institute\Documents\Neurexin_Paper\ALM 2P\Data\Controls"

session_list = [
    os.path.join(data_root, r"65.2a\2024_08_05_Switching"),
    os.path.join(data_root, r"65.2b\2024_07_31_Switching"),
    os.path.join(data_root, r"67.3b\2024_08_09_Switching"),
    os.path.join(data_root, r"67.3C\2024_08_20_Switching"),
    os.path.join(data_root, r"69.2a\2024_08_12_Switching"),
    os.path.join(data_root, r"72.3C\2024_09_10_Switching"),
]

set_lick_thresholds(session_list)


