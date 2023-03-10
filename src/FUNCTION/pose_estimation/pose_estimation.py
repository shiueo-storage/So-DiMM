from utils import global_path
import torch
from torchvision import transforms

from src.FUNCTION.pose_estimation.yolov7.utils.datasets import letterbox
from src.FUNCTION.pose_estimation.yolov7.utils.general import non_max_suppression_kpt
from src.FUNCTION.pose_estimation.yolov7.utils.plots import output_to_keypoint, plot_skeleton_kpts

import cv2
import numpy as np


class POSE_ESTIMATOR:
    def __init__(self):
        super(POSE_ESTIMATOR, self).__init__()

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(global_path.get_proj_abs_path("assets/models/yolov7-w6-pose.pt"), map_location=self.device)['model']

        self.model.float().eval()

        if torch.cuda.is_available():
            self.model.half().to(self.device)

        print(f"device: {self.device}, model loaded")

    def run_inference(self, image):
        image = letterbox(image, 960, stride=64, auto=True)[0]
        image = transforms.ToTensor()(image)

        if torch.cuda.is_available():
            image = image.half().to(self.device)

        image = image.unsqueeze(0)

        with torch.no_grad():
            output, _ = self.model(image)

        return output, image

    def draw_keypoints(self, output, image):
        output = non_max_suppression_kpt(output,
                                         0.25,  # Confidence Threshold
                                         0.65,  # IoU Threshold
                                         nc=self.model.yaml['nc'],  # Number of Classes
                                         nkpt=self.model.yaml['nkpt'],  # Number of Keypoints
                                         kpt_label=True)
        with torch.no_grad():
            output = output_to_keypoint(output)
        nimg = image[0].permute(1, 2, 0) * 255
        nimg = nimg.cpu().numpy().astype(np.uint8)
        nimg = cv2.cvtColor(nimg, cv2.COLOR_RGB2BGR)
        for idx in range(output.shape[0]):
            plot_skeleton_kpts(nimg, output[idx, 7:].T, 3)

        return nimg

    def pose_estimation_video(self, filename):
        cap = cv2.VideoCapture(filename)
        # VideoWriter for saving the video
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        out = cv2.VideoWriter('ice_skating_output.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
        while cap.isOpened():
            (ret, frame) = cap.read()
            if ret == True:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output, frame = self.run_inference(frame)
                frame = self.draw_keypoints(output, frame)
                frame = cv2.resize(frame, (int(cap.get(3)), int(cap.get(4))))
                out.write(frame)
                cv2.imshow('Pose estimation', frame)
            else:
                break

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()



