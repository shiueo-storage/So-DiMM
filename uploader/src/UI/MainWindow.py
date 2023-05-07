import copy
import datetime
import json
import hashlib
import os.path
import random

import urllib.request
import time
from pathlib import Path

import cv2
import numpy as np
import requests
from PySide6 import QtGui
from PySide6.QtCore import QThread, Slot, Signal, QTimer
from PySide6.QtGui import QPixmap, Qt, QFont
from requests_toolbelt import MultipartEncoder
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
    QPushButton,
    QLineEdit,
    QComboBox,
    QScrollArea,
    QFrame,
)
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

global ret, cv_img, CAM_WIDTH, CAM_HEIGHT, FILE_NAME, CAM_IMAGE, WEBCAM, WEBCAM_ON, REAL_CAM_WIDTH, REAL_CAM_HEIGHT, LANDMARK, DOWNLOADED_VIDEO_PATH, VID_LALABEL, VID_PLAYING, OPTION_BOX_2_RECORD_START_GLOB, DANCE_SELECTED_GLOB, CURRENT_DANCE_VIDEO_PATH_GLOB, OPTION_BOX_2_STATUS_LABEL_GLOB


class VIDEOTHREAD(QThread):
    change_pixmap_signal = Signal(np.ndarray)

    def run(self):
        global ret, cv_img, CAM_IMAGE, REAL_CAM_HEIGHT, REAL_CAM_WIDTH, LANDMARK
        cap = cv2.VideoCapture(0)
        REAL_CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        REAL_CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        with mp_pose.Pose(
                min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as pose:
            while cap.isOpened():
                success, image = cap.read()
                CAM_IMAGE = image
                CAM_IMAGE = image
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                LANDMARK = results.pose_landmarks
                # print(LANDMARK)

                # Draw the pose annotation on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )

                self.change_pixmap_signal.emit(image)
                # Flip the image horizontally for a selfie-view display.
                """
                cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break
                """
        cap.release()


class WEBCAP_GET(QThread):
    def run(self):
        prev_time = 0
        FPS = 30
        global CAM_IMAGE, WEBCAM, WEBCAM_ON, VID_PLAYING, OPTION_BOX_2_RECORD_START_GLOB, DANCE_SELECTED_GLOB, OPTION_BOX_2_STATUS_LABEL_GLOB
        while WEBCAM_ON and VID_PLAYING:
            # print(LANDMARK)
            current_time = time.time() - prev_time
            if current_time > 1.0 / FPS:
                prev_time = time.time()
                WEBCAM.write(CAM_IMAGE)
        WEBCAM.release()
        WEBCAM_ON = False
        OPTION_BOX_2_STATUS_LABEL_GLOB.setText(f"Recording Done")


class sodimm_uploader_UI_MainWindow(QMainWindow):
    def __init__(self):
        self.CAM_RECORDING_OUT = None
        global CAM_WIDTH, CAM_HEIGHT, WEBCAM_ON
        WEBCAM_ON = False
        super(sodimm_uploader_UI_MainWindow, self).__init__()
        font.load_font(w=self)
        with open(global_path.get_proj_abs_path("config/config.json"), "r") as j:
            self.config = json.load(j)

        self.DANCE_SELECTED = False
        self.CURRENT_DANCE_VIDEO_PATH = None
        global CURRENT_DANCE_VIDEO_PATH_GLOB
        CURRENT_DANCE_VIDEO_PATH_GLOB = self.CURRENT_DANCE_VIDEO_PATH
        global DANCE_SELECTED_GLOB
        DANCE_SELECTED_GLOB = self.DANCE_SELECTED

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

        self.VID_LABEL = QLabel()
        global VID_LALABEL
        VID_LALABEL = self.VID_LABEL

        self.CAM_V_BOX = QVBoxLayout()

        self.VIDEO_THREAD = VIDEOTHREAD()
        self.VIDEO_THREAD.change_pixmap_signal.connect(self.update_CAM)
        self.VIDEO_THREAD.start()

        self.OPTION_BOX_2 = QHBoxLayout()

        self.ID_LABEL = QLabel("ID:")
        self.ID_LABEL.setFont(QFont(self.Pretendard_SemiBold, 20))

        self.ID_INPUT = QLineEdit()
        self.ID_INPUT.setPlaceholderText("ID needed, max 8")
        self.ID_INPUT.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.ID_INPUT.setMaxLength(8)

        self.VID_NAME = QLineEdit()
        self.VID_NAME.setPlaceholderText("Video Name, max 16")
        self.VID_NAME.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.VID_NAME.setMaxLength(16)

        self.OPTION_BOX_2_STATUS_LABEL = QLabel()
        self.OPTION_BOX_2_STATUS_LABEL.setFont(QFont(self.Pretendard_SemiBold, 10))
        global OPTION_BOX_2_STATUS_LABEL_GLOB
        OPTION_BOX_2_STATUS_LABEL_GLOB = self.OPTION_BOX_2_STATUS_LABEL

        self.OPTION_BOX_2_RECORD_START = QPushButton("Record start")
        self.OPTION_BOX_2_RECORD_START.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.OPTION_BOX_2_RECORD_START.clicked.connect(lambda: self.RECORD_START())

        self.OPTION_BOX_2_RECORD_STOP = QPushButton("Record stop")
        self.OPTION_BOX_2_RECORD_STOP.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.OPTION_BOX_2_RECORD_STOP.setEnabled(False)
        self.OPTION_BOX_2_RECORD_STOP.clicked.connect(lambda: self.RECORD_STOP())

        self.UPLOAD_BOX = QPushButton("Upload")
        self.UPLOAD_BOX.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.UPLOAD_BOX.setEnabled(False)
        self.UPLOAD_BOX.clicked.connect(lambda: self.UPLOAD_BTN())

        global OPTION_BOX_2_RECORD_START_GLOB
        OPTION_BOX_2_RECORD_START_GLOB = self.OPTION_BOX_2_RECORD_START

        self.video_list = []
        self.API_HOST = "https://kaist.me/api/ksa/DS/api.php"
        self.get_video_list_param = {"apiName": ["list"]}

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
        self.CAM_V_BOX.addWidget(self.OPTION_BOX_2_STATUS_LABEL)
        self.CAM_V_BOX.addStretch(1)

        self.OPTION_BOX_2.addWidget(self.OPTION_BOX_2_RECORD_START)
        self.OPTION_BOX_2.addWidget(self.OPTION_BOX_2_RECORD_STOP)
        self.OPTION_BOX_2.addStretch(1)
        self.OPTION_BOX_2.addWidget(self.ID_LABEL)
        self.OPTION_BOX_2.addWidget(self.ID_INPUT)
        self.OPTION_BOX_2.addWidget(self.VID_NAME)
        self.OPTION_BOX_2.addWidget(self.UPLOAD_BOX)

        self.GRID.addLayout(self.CAM_V_BOX, 1, 0, 1, 1)
        self.GRID.addLayout(self.OPTION_BOX_2, 2, 0, 2, 1)

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

    def RECORD_START(self):
        if self.VID_NAME.text() and self.ID_INPUT.text():
            global CAM_WIDTH, CAM_HEIGHT, CAM_IMAGE, WEBCAM, WEBCAM_ON, REAL_CAM_WIDTH, REAL_CAM_HEIGHT, CURRENT_DANCE_VIDEO_PATH_GLOB, VID_PLAYING, FILE_NAME
            self.OPTION_BOX_2_RECORD_START.setEnabled(False)
            self.OPTION_BOX_2_RECORD_STOP.setEnabled(True)
            VID_PLAYING = True

            FILE_NAME = f"{self.VID_NAME.text()}"
            file_path = global_path.get_proj_abs_path(f"videos/{FILE_NAME}.mp4")
            self.CURRENT_DANCE_VIDEO_PATH = file_path
            CURRENT_DANCE_VIDEO_PATH_GLOB = file_path

            fourcc = cv2.VideoWriter_fourcc(*"MP4V")
            fps = 30

            size = (int(REAL_CAM_WIDTH), int(REAL_CAM_HEIGHT))

            WEBCAM = cv2.VideoWriter(file_path, fourcc, fps, size)
            WEBCAM_ON = True
            self.CAM_RECORDING_OUT = WEBCAP_GET()
            self.CAM_RECORDING_OUT.start()
            self.OPTION_BOX_2_STATUS_LABEL.setText(
                f"recording started\n{file_path[:len(file_path) // 2]}\n{file_path[len(file_path) // 2:]}"
            )
        else:
            self.OPTION_BOX_2_STATUS_LABEL.setText("we need id and vid name.")

    def RECORD_STOP(self):
        global CAM_WIDTH, CAM_HEIGHT, CAM_IMAGE, WEBCAM, WEBCAM_ON, REAL_CAM_WIDTH, REAL_CAM_HEIGHT, CURRENT_DANCE_VIDEO_PATH_GLOB, VID_PLAYING
        self.OPTION_BOX_2_RECORD_START.setEnabled(True)
        self.OPTION_BOX_2_RECORD_STOP.setEnabled(False)
        VID_PLAYING = False

        self.UPLOAD_BOX.setEnabled(True)

    def UPLOAD_BTN(self):
        global CURRENT_DANCE_VIDEO_PATH_GLOB, FILE_NAME
        self.UPLOAD_BOX.setEnabled(False)
        API_V_HOST = "https://kaist.me/api/ksa/DS/video.php"
        API_HOST = "https://kaist.me/api/ksa/DS/api.php"

        with open(CURRENT_DANCE_VIDEO_PATH_GLOB, "rb") as f:
            print(CURRENT_DANCE_VIDEO_PATH_GLOB)
            print(FILE_NAME)
            upload_vid_param = {"user_id": self.ID_INPUT.text(), "file": (FILE_NAME+".mp4", f, 'video')}

            try:

                m = MultipartEncoder(fields=upload_vid_param)
                headers = {'Content-Type': m.content_type}
                print(m.content_type)
                res = requests.post(API_V_HOST, headers=headers, data=m)
                self.OPTION_BOX_2_STATUS_LABEL.setText(res.text)
                print(res.text)
                print("upload done")

                response = requests.post(
                    API_HOST, params={"apiName": ["list"]}
                )
                content = response.json()
                print(content)

            except Exception as e:
                self.OPTION_BOX_2_STATUS_LABEL.setText(str(e))
