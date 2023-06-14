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

## 🧐 About <a name = "about"></a>
현대 사회에서는 코로나 사태로 인해 사람들의 움직임이 줄어들고, 직접 나가는 일과 대면 활동이 감소하고 있습니다. 이로 인해 운동 부족 문제가 심각해지고 있습니다. 본 프로젝트는 이러한 문제를 해결하기 위해 카메라가 장착된 컴퓨터 환경에서 실행 가능하고, 유행하는 춤을 따라하는 정확도를 평가하여 랭킹을 매길 수 있는 소프트웨어를 개발하는 것을 목표로 합니다.

## 🔧 전체 시스템 구성도
본 소프트웨어는 다음과 같은 단계로 구성되어 있습니다:
카메라 기반 동작 인식: 사용자의 움직임을 카메라로 실시간으로 촬영하여 동작을 인식합니다. 이를 위해 컴퓨터 비전 기술을 활용합니다.
따라하기 모드: 미리 등록된 유행하는 춤 등의 동작을 따라할 수 있는 모드를 제공합니다. 사용자가 동작을 따라하면 소프트웨어는 정확도를 측정하여 피드백을 제공합니다.
랭킹 시스템: 사용자들의 정확도를 기록하여 랭킹을 매깁니다. 이를 통해 사용자들은 자신의 실력 향상을 도모할 수 있습니다.

## 🎈 HW/SW 사양, 알고리즘
권장 HW
운영 체제: OS Independent
프로세서: 쿼드 코어 Intel 또는 AMD, 2.5GHz 이상
메모리: 4GB RAM
비디오 카드: NVIDIA GPU

알고리즘
카메라 기반 동작 인식:
CV2로 카메라 데이터 받기 -> global_frame_data의 실시간 frame의 데이터를 파악 -> mediapipe로 landmarks를 생성->landmarks데이터를 서버에서 받은 landmarks데이터와 각 점을 미분시킨 변화량의 차이를 비교 -> 점수로 표현

랭킹 시스템: 서버로부터 지금까지 기록된 유저들의 점수를 get -> sorting후 GUI에 표현



## 🚀 주된 특징 (장점) 과 추가로 더 발전시키고 싶은 부분 
지금까지 댄스배틀이나 따라하기 플랫폼으로써는 JustDance가 거의 유일한데, 이또한 장비가 없다면 폰을 흔들어서 그 자이로값만을 사용하기 때문에 제대로 된 춤을 비교할 수 없다는 단점이 있었으나, 저희의 So-DiMM은 전신을 파악하면서도 웹캠 외의 장비를 요하지 않기에 진입장벽을 매우 낮추었다는 장점이 있습니다.

추가로 발전시키고 싶은 부분으로는 MediaPipe보다 직접 LSTM을 사용해 파악 알고리즘을 구현해보고 싶습니다. Pytorch나 Tensorflow는 GPU-accelerated이기에 더욱 빠른 춤 파악기능을 제공할 수 있을 것입니다

## ✍️ Authors <a name = "authors"></a>
- [@shiueo](https://github.com/shiueo) - Frontend & Overall
- [@ileeric](https://github.com/ileeric) - Backend

See also the list of [contributors](https://github.com/shiueo-storage/So-DiMM/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- MediaPipe
- OpenCV
- Nuitka
