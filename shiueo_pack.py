import os
import json

from tools import build
from utils import global_path

global_path.set_proj_abs_path(os.path.abspath(__file__))

with open("config/config.json", "r") as j:
    config = json.load(j)

build.build(
    withconsole=False,
    path=os.path.abspath("SoDiMM.py"),
    file_dict=["assets", "config"],
    companyname="shiüo",
    product_version=config["version"],
    icon=global_path.get_proj_abs_path("assets/icon.png"),
    plugin_dict=["pyside6"],
    include_package_dict=[],
)
