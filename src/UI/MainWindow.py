import copy
import json

import cv2
import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import QThread, Slot, Signal, QTimer
from PySide6.QtGui import QPixmap, Qt, QFont
import subprocess

from utils import global_path
from src.UI.ui_utils import font
from src.UI.window import window
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout, QPushButton, QLineEdit, QComboBox,
)
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

global ret, cv_img, CAM_WIDTH, CAM_HEIGHT


class VIDEOTHREAD(QThread):
    change_pixmap_signal = Signal(np.ndarray)

    def run(self):
        global ret, cv_img
        cap = cv2.VideoCapture(0)
        with mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                LANDMARK = results.pose_landmarks
                print(LANDMARK)

                # Draw the pose annotation on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

                self.change_pixmap_signal.emit(image)
                # Flip the image horizontally for a selfie-view display.
                """
                cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break
                """
        cap.release()


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

        self.OPTION_BOX = QHBoxLayout()

        self.OPTION_BOX_LINEEDIT = QLineEdit()
        self.OPTION_BOX_LINEEDIT.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.OPTION_BOX_LINEEDIT.setPlaceholderText("Room ID")
        self.OPTION_BOX_JOIN_BTN = QPushButton("Join")
        self.OPTION_BOX_JOIN_BTN.setFont(QFont(self.Pretendard_SemiBold, 20))

        self.OPTION_BOX_2 = QHBoxLayout()
        self.OPTION_BOX_2_COMBO_BOX = QComboBox()
        self.OPTION_BOX_2_COMBO_BOX.setFont(QFont(self.Pretendard_SemiBold, 15))
        self.OPTION_BOX_2_COMBO_BOX.addItem("어쩔티비")
        self.OPTION_BOX_2_COMBO_BOX.addItem("awodih")

        self.OPTION_BOX_2_SELECT_BOX = QPushButton("Select")
        self.OPTION_BOX_2_SELECT_BOX.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.OPTION_BOX_2_START_BUTTON = QPushButton("Start")
        self.OPTION_BOX_2_START_BUTTON.setFont(QFont(self.Pretendard_SemiBold, 20))

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

        self.OPTION_BOX.addWidget(self.OPTION_BOX_LINEEDIT)
        self.OPTION_BOX.addWidget(self.OPTION_BOX_JOIN_BTN)

        self.OPTION_BOX_2.addWidget(self.OPTION_BOX_2_COMBO_BOX)
        self.OPTION_BOX_2.addWidget(self.OPTION_BOX_2_SELECT_BOX)
        self.OPTION_BOX_2.addWidget(self.OPTION_BOX_2_START_BUTTON)

        self.GRID.addLayout(self.CAM_V_BOX, 1, 0, 1, 1)
        self.GRID.addLayout(self.OPTION_BOX, 2, 0, 2, 1)
        self.GRID.addLayout(self.OPTION_BOX_2, 3, 0, 2, 1)
        self.GRID.addLayout(self.FOOTER_BOX, 4, 0, 1, 1)

    def updateUI(self):
        global CAM_WIDTH, CAM_HEIGHT
        CAM_WIDTH = self.widget.width() // 2
        CAM_HEIGHT = self.widget.height()
        self.OPTION_BOX_LINEEDIT.setMaximumWidth(self.widget.width() // 2)
        self.OPTION_BOX_2_COMBO_BOX.setMinimumWidth(self.widget.width() // 2)

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
