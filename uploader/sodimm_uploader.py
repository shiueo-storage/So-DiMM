import os
import sys

from PySide6.QtWidgets import QApplication

from src.UI.MainWindow import sodimm_uploader_UI_MainWindow
from utils import global_path

global_path.set_proj_abs_path(os.path.abspath(__file__))
sodimm_uploader_QApplication = QApplication()
sodimm_uploader_window = sodimm_uploader_UI_MainWindow()
sodimm_uploader_window.show()
sys.exit(sodimm_uploader_QApplication.exec())
