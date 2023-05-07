from PySide6.QtGui import QIcon

from utils import global_path


def setup(w):
    w.setWindowTitle("So-DiMM_UPLOADER")
    w.setWindowIcon(QIcon(global_path.get_proj_abs_path("assets/sodimm_icon.png")))
    w.setMinimumSize(600, 200)
    w.resize(1280, 720)
