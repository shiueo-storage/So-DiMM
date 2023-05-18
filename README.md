<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://github.com/shiueo-storage/So-DiMM/blob/main/assets/sodimm_icon.png?raw=true" alt="Project logo"></a>
</p>

<h3 align="center">So-DiMM</h3>

<div align="center">

  [![Status](https://img.shields.io/badge/status-active-success.svg)]() 
  [![GitHub Issues](https://img.shields.io/github/issues/shiueo-storage/So-DiMM.svg)](https://github.com/kylelobo/The-Documentation-Compendium/issues)
  [![GitHub Pull Requests](https://img.shields.io/github/issues-pr/shiueo-storage/So-DiMM.svg)](https://github.com/kylelobo/The-Documentation-Compendium/pulls)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Synchronize Other’s Dancing Instantaneously and get Motivated in Moving
    <br> 
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>
Currently, there are various approaches in the field of dance games. Some involve using VR devices to move the body, while others, such as Just Dance, require holding and moving a mobile phone. However, we have discovered that it is possible to capture joint movements using only a webcam. With this in mind, we have decided to create a user-friendly and convenient dance battle app that utilizes this method. By using the built-in webcam, users can easily and naturally perform dance moves.

Our project is divided into two parts: the Uploader client responsible for video uploads and the Discriminator client for dance analysis and scoring. If someone wants to upload their own dance, they can use the Uploader to submit their video to our server. On the other hand, the Discriminator client allows anyone to connect to the server from anywhere and receive scores for their dance performance.


## 🏁 Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites
There is [requirements.txt](https://github.com/shiueo-storage/So-DiMM/blob/main/requirements.txt) in the root folder. Just run 

```
pip install -r requirements.txt
```
That's all! Everything is perfectly set up for running the program!  

If you encounter any further issues, it is likely a problem with your virtual environment (venv) rather than the project itself. Please report any additional errors in the [Issues](https://github.com/shiueo-storage/So-DiMM/issues) section so that we can assist you further.

## 🔧 Running
Please navigate to the directory where the So-DiMM project is installed and execute the [SoDiMM.py](https://github.com/shiueo-storage/So-DiMM/blob/main/SoDiMM.py) file.

### Windows
```
python ./SoDiMM.py
```
or
```
python3 ./SoDiMM.py
```

### Mac

## 🎈 Usage <a name="usage"></a>
So-DiMM features a very simple and intuitive GUI.

## 🚀 Deployment <a name = "deployment"></a>
Add additional notes about how to deploy this on a live system.

## ⛏️ Built Using <a name = "built_using"></a>
- [Python](https://www.python.org/) - Language
- [Qt](https://www.qt.io/) - GUI Framework
- [Nuitka](https://github.com/Nuitka/Nuitka) - Packaging App
- [MediaPipe](https://google.github.io/mediapipe/) - for the Pose Detection
- [PHP](https://www.php.net/) - PHP
- [NodeJs](https://nodejs.org/en/) - Server Environment

## ✍️ Authors <a name = "authors"></a>
- [@shiueo](https://github.com/shiueo) - Frontend & Overall
- [@ileeric](https://github.com/ileeric) - Backend

See also the list of [contributors](https://github.com/shiueo-storage/So-DiMM/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- MediaPipe
- OpenCV
- Nuitka
