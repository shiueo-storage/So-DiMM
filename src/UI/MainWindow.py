import copy
import json

import cv2
import numpy as np
import torch
from PySide6 import QtGui
from PySide6.QtCore import QThread, Slot, Signal, QTimer
from PySide6.QtGui import QPixmap, Qt, QFont

from src.FUNCTION.pose_estimation.pose_src import util
from src.FUNCTION.pose_estimation.pose_src.body import Body
from src.FUNCTION.pose_estimation.pose_src.hand import Hand
from utils import global_path
from src.UI.ui_utils import font
from src.UI.window import window
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow, QVBoxLayout,
)

global ret, cv_img, CAM_WIDTH, CAM_HEIGHT, body_estimation, hand_estimation
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


class POSED_CAM_THREAD(QThread):
    update_posed_CAM = Signal(np.ndarray)

    def run(self):
        global ret, cv_img, body_estimation, hand_estimation
        while 1:
            if ret:
                candidate, subset = body_estimation(cv_img)
                canvas = copy.deepcopy(cv_img)
                canvas = util.draw_bodypose(canvas, candidate, subset)

                # detect hand
                hands_list = util.handDetect(candidate, subset, cv_img)

                all_hand_peaks = []
                for x, y, w, is_left in hands_list:
                    peaks = hand_estimation(cv_img[y: y + w, x: x + w, :])
                    peaks[:, 0] = np.where(peaks[:, 0] == 0, peaks[:, 0], peaks[:, 0] + x)
                    peaks[:, 1] = np.where(peaks[:, 1] == 0, peaks[:, 1], peaks[:, 1] + y)
                    all_hand_peaks.append(peaks)

                canvas = util.draw_handpose(canvas, all_hand_peaks)

                rgb_image = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(CAM_WIDTH, CAM_HEIGHT, Qt.KeepAspectRatio)
                p = QPixmap.fromImage(p)

                self.update_posed_CAM.emit(p)
            else:
                print("CAM Not initialized yet.")


class sodimm_UI_MainWindow(QMainWindow):
    def __init__(self):
        global CAM_WIDTH, CAM_HEIGHT, body_estimation, hand_estimation
        super(sodimm_UI_MainWindow, self).__init__()
        font.load_font(w=self)
        with open(global_path.get_proj_abs_path("config/config.json"), "r") as j:
            self.config = json.load(j)

        print(f"Torch device: {torch.cuda.get_device_name()}")
        body_estimation = Body(
            global_path.get_proj_abs_path("assets/models/body_pose_model.pth")
        )

        hand_estimation = Hand(
            global_path.get_proj_abs_path("assets/models/hand_pose_model.pth")
        )

        self.widget = QWidget()
        window.setup(w=self)

        """
        self.estimator = pose_estimation.Pose_Estimator(need_test=True)
        self.estimator.video_estimate(
            global_path.get_proj_abs_path("test/test_video.mp4")
        )
        """

        self.GRID = QGridLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.CAM_W_TEXT = QLabel("CAM:0")
        self.CAM_W_TEXT.setFont(QFont(self.Pretendard_SemiBold, 20))

        self.CAM_LABEL = QLabel()
        CAM_WIDTH = 512
        CAM_HEIGHT = 512
        self.CAM_LABEL.resize(CAM_WIDTH, CAM_HEIGHT)

        self.CAM_V_BOX = QVBoxLayout()

        self.VIDEO_THREAD = VIDEOTHREAD()
        self.VIDEO_THREAD.change_pixmap_signal.connect(self.update_CAM)
        self.VIDEO_THREAD.start()

        self.POSED_CAM_BOX = QLabel()

        self.POSED_VIDEO_THREAD = POSED_CAM_THREAD()
        self.POSED_VIDEO_THREAD.update_posed_CAM.connect(self.update_posed_CAM)
        self.POSED_VIDEO_THREAD.start()

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
        self.CAM_V_BOX.addWidget(self.POSED_CAM_BOX)

        self.FOOTER_BOX.addWidget(self.FOOTER_LABEL)

        self.GRID.addLayout(self.CAM_V_BOX, 1, 0, 1, 1)
        self.GRID.addLayout(self.FOOTER_BOX, 3, 0, 1, 1)

    def updateUI(self):
        global CAM_WIDTH, CAM_HEIGHT
        CAM_WIDTH = self.widget.width() // 2
        CAM_HEIGHT = self.widget.height() // 2

    @Slot(np.ndarray)
    def update_CAM(self, cv_img):
        """Updates the CAM_LABEL with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.CAM_LABEL.setPixmap(qt_img)

    @Slot(np.ndarray)
    def update_posed_CAM(self, cv_img):
        self.POSED_CAM_BOX.setPixmap(cv_img)

    def convert_cv_qt(self, cv_img):
        global CAM_WIDTH, CAM_HEIGHT
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(CAM_WIDTH, CAM_HEIGHT, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
