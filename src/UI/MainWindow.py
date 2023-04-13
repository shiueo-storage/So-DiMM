import copy
import json

import cv2
import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import QThread, Slot, Signal, QTimer
from PySide6.QtGui import QPixmap, Qt, QFont

from utils import global_path
from src.UI.ui_utils import font
from src.UI.window import window
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
)

global ret, cv_img, CAM_WIDTH, CAM_HEIGHT
ret = None
cv_img = None


class VIDEOTHREAD(QThread):
    change_pixmap_signal = Signal(np.ndarray)

    def run(self):
        global ret, cv_img
        cap = cv2.VideoCapture(0)
        while 1:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)


class sodimm_UI_MainWindow(QMainWindow):
    def __init__(self):
        global CAM_WIDTH, CAM_HEIGHT
        super(sodimm_UI_MainWindow, self).__init__()
        font.load_font(w=self)
        with open(global_path.get_proj_abs_path("config/config.json"), "r") as j:
            self.config = json.load(j)

        self.widget = QWidget()
        window.setup(w=self)

        self.ERROR_PNG = QPixmap()
        self.ERROR_PNG.load(global_path.get_proj_abs_path("assets/error.png"))

        self.GRID = QGridLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.CAM_W_TEXT = QLabel("Your CAM")
        self.CAM_W_TEXT.setFont(QFont(self.Pretendard_SemiBold, 20))

        self.CAM_LABEL = QLabel()
        CAM_WIDTH = 512
        CAM_HEIGHT = 512
        self.CAM_LABEL.resize(CAM_WIDTH, CAM_HEIGHT)

        self.CAM_LABEL.setPixmap(self.ERROR_PNG)

        self.CAM_V_BOX = QVBoxLayout()

        self.VIDEO_THREAD = VIDEOTHREAD()
        self.VIDEO_THREAD.change_pixmap_signal.connect(self.update_CAM)
        self.VIDEO_THREAD.start()

        self.FOOTER_BOX = QHBoxLayout()
        self.FOOTER_LABEL = QLabel(
            f"Copyright (c) 2023- shiüo & ileeric :: So-DiMM v{self.config['version']}"
        )

        self.timer = QTimer(self)
        self.timer.setInterval(1000 / 2)
        self.timer.timeout.connect(lambda: self.updateUI())
        self.timer.start()

        self.initUI()

    def initUI(self):
        with open(
            file=global_path.get_proj_abs_path("assets/stylesheet.txt"), mode="r"
        ) as f:
            self.setStyleSheet(f.read())

        self.CAM_V_BOX.addWidget(self.CAM_W_TEXT)
        self.CAM_V_BOX.addWidget(self.CAM_LABEL)

        self.FOOTER_BOX.addWidget(self.FOOTER_LABEL)

        self.GRID.addLayout(self.CAM_V_BOX, 1, 0, 1, 1)
        self.GRID.addLayout(self.FOOTER_BOX, 3, 0, 1, 1)

    def updateUI(self):
        global CAM_WIDTH, CAM_HEIGHT
        CAM_WIDTH = self.widget.width()
        CAM_HEIGHT = self.widget.height()

    @Slot(np.ndarray)
    def update_CAM(self, cv_img):
        """Updates the CAM_LABEL with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.CAM_LABEL.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        global CAM_WIDTH, CAM_HEIGHT
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
        )
        p = convert_to_Qt_format.scaled(CAM_WIDTH, CAM_HEIGHT, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
