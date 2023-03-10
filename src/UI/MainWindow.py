import json
import webbrowser

from PySide6.QtCore import QTimer

from src.FUNCTION.pose_estimation import pose_estimation
from utils import global_path
from src.UI.menubar import menubar
from src.UI.window import window
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMainWindow,
)


class sodimm_UI_MainWindow(QMainWindow):
    def __init__(self):
        super(sodimm_UI_MainWindow, self).__init__()
        with open(global_path.get_proj_abs_path("config/config.json"), "r") as j:
            self.config = json.load(j)

        widget = QWidget()
        menubar.setup(w=self)
        window.setup(w=self)

        self.estimator = pose_estimation.Pose_Estimator(need_test=True)
        self.estimator.video_estimate(
            global_path.get_proj_abs_path("assets/test/test_video.mp4")
        )
        self.GRID = QGridLayout(widget)
        self.setCentralWidget(widget)

        self.FOOTER_BOX = QHBoxLayout()
        self.FOOTER_LABEL = QLabel(
            f"Copyright (c) 2023- shiüo & ileeric :: So-DiMM v{self.config['version']}"
        )

        self.initUI()

    def initUI(self):
        with open(
            file=global_path.get_proj_abs_path("assets/stylesheet.txt"), mode="r"
        ) as f:
            self.setStyleSheet(f.read())

        self.FOOTER_BOX.addWidget(self.FOOTER_LABEL)

        self.GRID.addLayout(self.FOOTER_BOX, 3, 0, 1, 1)
