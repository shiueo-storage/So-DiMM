import cv2
import matplotlib.pyplot as plt
import copy
import numpy as np
import torch

from src.FUNCTION.pose_estimation.pytorch_pose_estimator.pose_src import model
from src.FUNCTION.pose_estimation.pytorch_pose_estimator.pose_src import util
from src.FUNCTION.pose_estimation.pytorch_pose_estimator.pose_src.body import Body
from src.FUNCTION.pose_estimation.pytorch_pose_estimator.pose_src.hand import Hand
from utils import global_path

'''
body_estimation = Body(
    global_path.get_proj_abs_path("assets/models/body_pose_model.pth")
)'''
body_estimation = Body("D:\Github/So-DiMM/assets/models/body_pose_model.pth")
'''
hand_estimation = Hand(
    global_path.get_proj_abs_path("assets/models/hand_pose_model.pth")
)'''
hand_estimation = Hand("D:\Github/So-DiMM/assets/models/hand_pose_model.pth")

print(f"Torch device: {torch.cuda.get_device_name()}")

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
while True:
    ret, oriImg = cap.read()

    candidate, subset = body_estimation(oriImg)
    canvas = copy.deepcopy(oriImg)
    canvas = util.draw_bodypose(canvas, candidate, subset)

    # detect hand
    hands_list = util.handDetect(candidate, subset, oriImg)

    all_hand_peaks = []
    for x, y, w, is_left in hands_list:
        peaks = hand_estimation(oriImg[y : y + w, x : x + w, :])
        peaks[:, 0] = np.where(peaks[:, 0] == 0, peaks[:, 0], peaks[:, 0] + x)
        peaks[:, 1] = np.where(peaks[:, 1] == 0, peaks[:, 1], peaks[:, 1] + y)
        all_hand_peaks.append(peaks)

    canvas = util.draw_handpose(canvas, all_hand_peaks)

    cv2.imshow("demo", canvas)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()