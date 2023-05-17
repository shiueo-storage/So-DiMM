import copy
import datetime
import json
import hashlib
import os.path
import pathlib
import pprint
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

from src.FUNCTION.pose_estimation import video_to_pose_data
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
import playsound

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

global FPS, CURRENT_RANKING, CAM_W_TEXT_GLOB, ret, DATA1, GLOBAL_ID_INPUT, DATA2, MIN_LEN_DATA, cv_img, CAM_WIDTH, CAM_HEIGHT, JUMSOO_THREAD, CAM_IMAGE, WEBCAM, WEBCAM_ON, REAL_CAM_WIDTH, REAL_CAM_HEIGHT, LANDMARK, DOWNLOADED_VIDEO_PATH, VID_LALABEL, VID_PLAYING, OPTION_BOX_2_RECORD_START_GLOB, DANCE_SELECTED_GLOB, CURRENT_DANCE_VIDEO_PATH_GLOB, OPTION_BOX_2_STATUS_LABEL_GLOB


class SOUND_PLAYER(QThread):
    def run(self):
        playsound.playsound(global_path.get_proj_abs_path("assets/zerotwou.wav"))


class VIDEO_PLAYER(QThread):
    global FPS

    def run(self):
        print(FPS)
        print("started")
        prev_time = 0

        global DOWNLOADED_VIDEO_PATH, VID_LALABEL, CAM_WIDTH, CAM_HEIGHT, VID_PLAYING, OPTION_BOX_2_RECORD_START_GLOB
        VID_PLAYING = True
        print(DOWNLOADED_VIDEO_PATH)
        cap = cv2.VideoCapture(DOWNLOADED_VIDEO_PATH)
        print(cap.isOpened)
        OPTION_BOX_2_RECORD_START_GLOB.setEnabled(False)
        while cap.isOpened():
            current_time = time.time() - prev_time
            if current_time > 1.0 / FPS:
                prev_time = time.time()
                ret, frame = cap.read()
                if not ret:
                    break

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_image = cv2.flip(rgb_image, 1)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QtGui.QImage(
                    rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
                )
                p = convert_to_Qt_format.scaled(CAM_WIDTH, CAM_HEIGHT, Qt.KeepAspectRatio)
                VID_LALABEL.setPixmap(QPixmap.fromImage(p))

        cap.release()
        print("video played")
        OPTION_BOX_2_RECORD_START_GLOB.setEnabled(True)
        VID_PLAYING = False


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
                image = cv2.flip(image, 1)
                self.change_pixmap_signal.emit(image)
                # Flip the image horizontally for a selfie-view display.
                """
                cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break
                """
        cap.release()


class JUMSOO(QThread):
    global DATA1, DATA2, MIN_LEN_DATA, CAM_W_TEXT_GLOB, CAM_WIDTH, CAM_HEIGHT, GLOBAL_ID_INPUT, DOWNLOADED_VIDEO_PATH

    def run(self):
        s = 0
        print("score!")
        WHOLE_LEN = MIN_LEN_DATA * 33  # MP NUM
        print(WHOLE_LEN)
        print(MIN_LEN_DATA)
        for i in range(33):
            for j in range(MIN_LEN_DATA):
                x_v = (1 - abs(DATA1[i][0][j] - DATA2[i][0][j])) ** 4
                y_v = (1 - abs(DATA1[i][1][j] - DATA2[i][1][j])) ** 4
                s += x_v + y_v
        score = (s / (WHOLE_LEN * 2)) * 100
        print(s / (WHOLE_LEN * 2))
        CAM_W_TEXT_GLOB.setText(f"SCORE: {score}")
        if GLOBAL_ID_INPUT.text():
            print(GLOBAL_ID_INPUT.text(), pathlib.Path(DOWNLOADED_VIDEO_PATH).stem)
            param = {"apiName": "uploadScore", "user_id": str(GLOBAL_ID_INPUT.text()),
                     "filename": str(pathlib.Path(DOWNLOADED_VIDEO_PATH).stem), "score": str(score)}
            try:
                response = requests.post("https://kaist.me/api/ksa/DS/api.php", data=param)
                print(response.status_code)
            except Exception as e:
                print(e)


class WEBCAP_GET(QThread):
    def run(self):
        prev_time = 0
        FPS = 30
        global CAM_IMAGE, DATA1, DATA2, MIN_LEN_DATA, WEBCAM, WEBCAM_ON, VID_PLAYING, OPTION_BOX_2_RECORD_START_GLOB, DANCE_SELECTED_GLOB, OPTION_BOX_2_STATUS_LABEL_GLOB, CURRENT_DANCE_VIDEO_PATH_GLOB
        while WEBCAM_ON and VID_PLAYING:
            # print(LANDMARK)
            current_time = time.time() - prev_time
            if current_time > 1.0 / FPS:
                prev_time = time.time()
                WEBCAM.write(CAM_IMAGE)
        WEBCAM.release()
        WEBCAM_ON = False
        OPTION_BOX_2_STATUS_LABEL_GLOB.setText(f"Recording Done")
        print(CURRENT_DANCE_VIDEO_PATH_GLOB)
        print("running detetctor")
        DATA1 = video_to_pose_data.convert(CURRENT_DANCE_VIDEO_PATH_GLOB, dev=True)
        DATA2 = video_to_pose_data.convert(DOWNLOADED_VIDEO_PATH, dev=True)
        len_data1 = len(DATA1[0][0])
        len_data2 = len(DATA2[0][0])

        MIN_LEN_DATA = min(len_data1, len_data2)
        JUMSOO_THREAD.start()


class sodimm_UI_MainWindow(QMainWindow):
    def __init__(self):
        global CAM_WIDTH, CAM_HEIGHT, WEBCAM_ON, VID_PLAYING, JUMSOO_THREAD, CAM_W_TEXT_GLOB, GLOBAL_ID_INPUT, CURRENT_RANKING, FPS
        FPS = 30

        self.SOUNDER = SOUND_PLAYER()
        CURRENT_RANKING = []
        JUMSOO_THREAD = JUMSOO()
        VID_PLAYING = False
        WEBCAM_ON = False
        super(sodimm_UI_MainWindow, self).__init__()
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

        self.CAM_W_TEXT = QLabel("SCORE: NULL")
        self.CAM_W_TEXT.setFont(QFont(self.Pretendard_SemiBold, 20))

        self.CAM_W_ID_LABEL = QLabel("ID:")
        self.CAM_W_ID_LABEL.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.CAM_W_ID_INPUT = QLineEdit("ANON")
        self.CAM_W_ID_INPUT.setMaximumWidth(150)
        self.CAM_W_ID_INPUT.setPlaceholderText("ID")
        self.CAM_W_ID_INPUT.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.CAM_W_ID_INPUT.setMaxLength(8)

        CAM_W_TEXT_GLOB = self.CAM_W_TEXT

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

        self.VID_PLAYER_THREAD = VIDEO_PLAYER()

        self.OPTION_BOX = QHBoxLayout()

        self.OPTION_BOX_SELECT_INDICATOR = QLabel("None")
        self.OPTION_BOX_SELECT_INDICATOR.setFont(QFont(self.Pretendard_SemiBold, 20))

        self.OPTION_BOX_SELECT_VIDEO_PLAY = QPushButton("Play")
        self.OPTION_BOX_SELECT_VIDEO_PLAY.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.OPTION_BOX_SELECT_VIDEO_PLAY.clicked.connect(lambda: self.VIDEO_PLAY())

        self.OPTION_BOX_2 = QHBoxLayout()

        self.OPTION_BOX_2_STATUS_LABEL = QLabel()
        self.OPTION_BOX_2_STATUS_LABEL.setFont(QFont(self.Pretendard_SemiBold, 10))
        global OPTION_BOX_2_STATUS_LABEL_GLOB
        OPTION_BOX_2_STATUS_LABEL_GLOB = self.OPTION_BOX_2_STATUS_LABEL

        self.OPTION_BOX_2_RECORD_START = QPushButton("Record start")
        self.OPTION_BOX_2_RECORD_START.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.OPTION_BOX_2_RECORD_START.clicked.connect(lambda: self.RECORD_START())

        global OPTION_BOX_2_RECORD_START_GLOB
        OPTION_BOX_2_RECORD_START_GLOB = self.OPTION_BOX_2_RECORD_START

        self.RIGHT_GRID = QVBoxLayout()

        self.RIGHT_NAME_BOX = QHBoxLayout()

        self.RELOAD_BTN = QPushButton("Refresh")
        self.RELOAD_BTN.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.RELOAD_BTN.clicked.connect(lambda: self.REFRESH_CLICKED())

        self.BACKTO_BTN = QPushButton("Back")
        self.BACKTO_BTN.setFont(QFont(self.Pretendard_SemiBold, 20))
        self.BACKTO_BTN.clicked.connect(lambda: self.BACKTO_BTN_CLICKED())
        self.BACKTO_BTN.setEnabled(False)

        self.video_list = []
        self.API_HOST = "https://kaist.me/api/ksa/DS/api.php"
        self.get_video_list_param = {"apiName": ["list"]}

        self.video_scroll_area = QScrollArea()
        self.video_widget = QWidget()
        self.video_ui = QVBoxLayout()
        self.video_scroll_area.setWidget(self.video_widget)
        self.video_widget.setLayout(self.video_ui)
        self.video_scroll_area.setWidgetResizable(True)

        self.ranking_video_scroll_area = QScrollArea()
        self.ranking_video_widget = QWidget()
        self.ranking_video_ui = QVBoxLayout()
        self.ranking_video_scroll_area.setWidget(self.ranking_video_widget)
        self.ranking_video_widget.setLayout(self.ranking_video_ui)
        self.ranking_video_scroll_area.setWidgetResizable(True)

        self.CAM_H_2_BOX = QHBoxLayout()

        self.video_ui_button_list = {}

        self.CAM_RECORDING_OUT = None

        self.timer = QTimer(self)
        self.timer.setInterval(1000 / 2)
        self.timer.timeout.connect(lambda: self.updateUI())
        self.timer.start()
        GLOBAL_ID_INPUT = self.CAM_W_ID_INPUT

        self.initUI()

    def initUI(self):
        with open(
                file=global_path.get_proj_abs_path("assets/stylesheet.txt"), mode="r"
        ) as f:
            self.setStyleSheet(f.read())

        self.CAM_V_BOX.addWidget(self.CAM_W_TEXT)
        self.CAM_V_BOX.addWidget(self.CAM_W_ID_INPUT)
        self.CAM_V_BOX.addLayout(self.CAM_H_2_BOX)
        self.CAM_V_BOX.addWidget(self.CAM_LABEL)
        self.CAM_V_BOX.addWidget(self.OPTION_BOX_2_STATUS_LABEL)
        self.CAM_V_BOX.addStretch(1)

        self.OPTION_BOX.addWidget(self.OPTION_BOX_SELECT_INDICATOR)
        self.OPTION_BOX.addWidget(self.OPTION_BOX_SELECT_VIDEO_PLAY)

        self.OPTION_BOX_2.addWidget(self.OPTION_BOX_2_RECORD_START)

        self.RIGHT_NAME_BOX.addWidget(self.RELOAD_BTN)
        self.RIGHT_NAME_BOX.addWidget(self.BACKTO_BTN)
        self.RIGHT_GRID.addLayout(self.RIGHT_NAME_BOX)
        self.RIGHT_GRID.addWidget(self.video_scroll_area)
        self.RIGHT_GRID.addWidget(self.ranking_video_scroll_area)

        self.GRID.addLayout(self.CAM_V_BOX, 1, 0, 1, 1)
        self.GRID.addLayout(self.OPTION_BOX_2, 2, 0, 2, 1)
        self.GRID.addLayout(self.RIGHT_GRID, 1, 1, 1, 1)
        self.GRID.addLayout(self.OPTION_BOX, 2, 1, 2, 1)

    def REFRESH_CLICKED(self):
        self.video_list.clear()
        for i in reversed(range(self.video_ui.count() - 1)):
            self.video_ui.takeAt(i).widget().setParent(None)
        self.video_ui.takeAt(0)
        try:
            response = requests.post(self.API_HOST, params=self.get_video_list_param)
            content = response.json()
            for i in content:
                c = [i["i"], i["user_id"], i["filename"]]
                self.video_list.append(c)
            print(self.video_list)
            for i in self.video_list:
                QQQ = QHBoxLayout()
                Q = QPushButton(f"{i[1]} - {Path(i[2]).stem}")
                Q.setFont(QFont(self.Pretendard_SemiBold, 20))
                Q.clicked.connect(self.Q_BTN_CLICKED)
                Q_RANKING = QPushButton("Ranking update")
                Q_RANKING.setFont(QFont(self.Pretendard_SemiBold, 20))
                Q_RANKING.clicked.connect(self.Q_RANKING_BTN_CLICKED)
                Q_RANKING.setObjectName(f"{i[1]} - {Path(i[2]).stem}")
                self.video_ui_button_list[f"{i[1]} - {Path(i[2]).stem}"] = i[2]
                QQQ.addWidget(Q)
                QQQ.addWidget(Q_RANKING)
                self.video_ui.addLayout(QQQ)
            self.video_ui.addStretch(1)
        except Exception as e:
            error = QLabel(str(e))
            error.setFont(QFont(self.Pretendard_SemiBold, 20))
            self.video_ui.addWidget(error)

    def Q_RANKING_BTN_CLICKED(self):
        btn = self.sender()
        global CURRENT_RANKING
        print(btn.objectName())
        try:
            param = {"apiName": "getRanking", "filename": btn.objectName()}
            response = requests.post("https://kaist.me/api/ksa/DS/api.php", data=param)
            print(response.json())
            CURRENT_RANKING = response.json()
            for i in reversed(range(self.ranking_video_ui.count() - 1)):
                self.ranking_video_ui.takeAt(i).widget().setParent(None)
            self.ranking_video_ui.takeAt(0)

            for i in CURRENT_RANKING:
                w = QPushButton(f"{i['user_id']}: {i['score']}")
                w.setFont(QFont(self.Pretendard_SemiBold, 20))
                self.ranking_video_ui.addWidget(w)
            self.ranking_video_ui.addStretch(1)
        except Exception as e:
            print(e)

    def Q_BTN_CLICKED(self):
        global DOWNLOADED_VIDEO_PATH, VID_LALABEL
        self.BACKTO_BTN.setEnabled(True)
        btn = self.sender()
        print(self.video_ui_button_list[btn.text()])
        self.OPTION_BOX_SELECT_INDICATOR.setText(btn.text())
        try:
            savename = global_path.get_proj_abs_path(f"videos_e/{btn.text()}.mp4")
            urllib.request.urlretrieve(self.video_ui_button_list[btn.text()], savename)
            self.OPTION_BOX_2_STATUS_LABEL.setText(
                f"{self.video_ui_button_list[btn.text()]} Downloaded!"
            )
            self.DANCE_SELECTED = True
            self.video_scroll_area.setParent(None)
            self.ranking_video_scroll_area.setParent(None)
            self.RIGHT_GRID.addWidget(self.VID_LABEL)
            print("dance selected")
            DOWNLOADED_VIDEO_PATH = savename
            self.VID_LABEL.setText("VIDEO LOADED.")
            self.OPTION_BOX_2_RECORD_START.setEnabled(True)

        except Exception as e:
            self.OPTION_BOX_2_RECORD_START.setEnabled(False)
            self.OPTION_BOX_2_STATUS_LABEL.setText(str(e))

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def BACKTO_BTN_CLICKED(self):
        self.VID_LABEL.setParent(None)
        self.RIGHT_GRID.addWidget(self.video_scroll_area)
        self.RIGHT_GRID.addWidget(self.ranking_video_scroll_area)
        self.BACKTO_BTN.setEnabled(False)
        self.DANCE_SELECTED = False
        self.OPTION_BOX_2_RECORD_START.setEnabled(False)

    def VIDEO_PLAY(self):
        print("thread on")
        global FPS
        FPS = 24
        self.VID_PLAYER_THREAD.start()
        self.SOUNDER.start()

        print("running")

    def updateUI(self):
        global CAM_WIDTH, CAM_HEIGHT
        CAM_WIDTH = self.widget.width() // 2
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
        global CAM_WIDTH, CAM_HEIGHT, CAM_IMAGE, WEBCAM, WEBCAM_ON, REAL_CAM_WIDTH, REAL_CAM_HEIGHT, CURRENT_DANCE_VIDEO_PATH_GLOB, VID_PLAYING, FPS
        FPS = 29
        if self.DANCE_SELECTED:
            self.OPTION_BOX_2_RECORD_START.setEnabled(False)

            file_name = hashlib.sha256(
                (
                        str(datetime.datetime.now()).replace(" ", "")
                        + str(random.randrange(0, 10000000))
                ).encode()
            ).hexdigest()
            file_path = global_path.get_proj_abs_path(f"videos/{file_name}.mp4")
            self.CURRENT_DANCE_VIDEO_PATH = file_path
            CURRENT_DANCE_VIDEO_PATH_GLOB = file_path

            fourcc = cv2.VideoWriter_fourcc(*"MP4V")
            fps = 30

            size = (int(REAL_CAM_WIDTH), int(REAL_CAM_HEIGHT))

            WEBCAM = cv2.VideoWriter(file_path, fourcc, fps, size)
            WEBCAM_ON = True
            self.CAM_RECORDING_OUT = WEBCAP_GET()
            self.VID_PLAYER_THREAD.start()
            self.SOUNDER.start()
            VID_PLAYING = True
            self.CAM_RECORDING_OUT.start()
            self.OPTION_BOX_2_STATUS_LABEL.setText(
                f"recording started\n{file_path[:len(file_path) // 2]}\n{file_path[len(file_path) // 2:]}"
            )

        else:
            self.OPTION_BOX_2_STATUS_LABEL.setText("Dance not selected")
