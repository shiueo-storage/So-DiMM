import os
import sys

from PySide6.QtWidgets import QApplication

from src.UI.MainWindow import sodimm_UI_MainWindow
from utils import global_path

global_path.set_proj_abs_path(os.path.abspath(__file__))
sodimm_QApplication = QApplication()
sodimm_window = sodimm_UI_MainWindow()
sodimm_window.show()
sys.exit(sodimm_QApplication.exec())
