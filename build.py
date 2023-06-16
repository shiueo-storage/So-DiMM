"""
The MIT License (MIT)

Copyright (c) 2023-present shiüo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
import json

from tools import build
from utils import global_path

global_path.set_proj_abs_path(os.path.abspath(__file__))

with open("config/config.json", "r") as j:
    config = json.load(j)

build.build(
    withconsole=True,
    path=os.path.abspath("SoDiMM.py"),
    file_dict=["assets", "config", "videos", "videos_e"],
    companyname="shiüo+ileeric",
    product_version=config["version"],
    icon=global_path.get_proj_abs_path("assets/sodimm_icon.png"),
    plugin_dict=["pyside6"],
    include_package_dict=["mediapipe"],
)

"""
python -m nuitka --clang --show-modules --follow-imports --windows-company-name=shiüo+ileeric --windows-product-version=1.0.3 --output-dir=D:\Github\So-DiMM\SoDiMM_build --verbose --assume-yes-for-downloads --enable-plugin=pyside6 --include-package=mediapipe --windows-icon-from-ico=D:\Github\So-DiMM\assets/sodimm_icon.png D:\Github\So-DiMM\SoDiMM.py
"""
