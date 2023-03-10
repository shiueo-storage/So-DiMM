import subprocess

import cv2
from PIL import Image

from src.FUNCTION.deface import deface
from utils import global_path

LOW_RES_WH = 256


class Pose_Estimator:
    def __init__(self, need_test=False):
        super(Pose_Estimator, self).__init__()
        self.BODY_PARTS = {
            "Head": 0,
            "Neck": 1,
            "RShoulder": 2,
            "RElbow": 3,
            "RWrist": 4,
            "LShoulder": 5,
            "LElbow": 6,
            "LWrist": 7,
            "RHip": 8,
            "RKnee": 9,
            "RAnkle": 10,
            "LHip": 11,
            "LKnee": 12,
            "LAnkle": 13,
            "Chest": 14,
            "Background": 15,
        }

        self.POSE_PAIRS = [
            ["Head", "Neck"],
            ["Neck", "RShoulder"],
            ["RShoulder", "RElbow"],
            ["RElbow", "RWrist"],
            ["Neck", "LShoulder"],
            ["LShoulder", "LElbow"],
            ["LElbow", "LWrist"],
            ["Neck", "Chest"],
            ["Chest", "RHip"],
            ["RHip", "RKnee"],
            ["RKnee", "RAnkle"],
            ["Chest", "LHip"],
            ["LHip", "LKnee"],
            ["LKnee", "LAnkle"],
        ]

        self.protoFile = global_path.get_proj_abs_path(
            "assets/models/pose_deploy_linevec.prototxt"
        )
        self.weightsFile = global_path.get_proj_abs_path(
            "assets/models/pose_iter_440000.caffemodel"
        )

        self.net = cv2.dnn.readNetFromCaffe(self.protoFile, self.weightsFile)
        self.need_test = need_test
        print("model loaded")

    def video_estimate(self, video):
        cap = cv2.VideoCapture(video)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        frame_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(frame_num, fps)

        out = cv2.VideoWriter(
            "./test/test_video.mp4",
            fourcc,
            fps,
            (LOW_RES_WH, LOW_RES_WH),
        )

        frame_count = 0
        while cap.isOpened():
            (ret, frame) = cap.read()
            frame_count += 1
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = self.image_estimate(frame)
                if self.need_test:
                    cv2.imshow("asdasd", frame)
                    cv2.waitKey(10)
                    out.write(frame)
                print(f"FRAME: {frame_count} / {frame_num}")
            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        deface.video_deface("./test/test_video.mp4")
        print("defacing end")

        print("done")

    def image_estimate(self, image):
        image = cv2.resize(image, (LOW_RES_WH, LOW_RES_WH))
        image_Blob = cv2.dnn.blobFromImage(
            image,
            1.0 / 255,
            (LOW_RES_WH, LOW_RES_WH),
            (0, 0, 0),
            swapRB=False,
            crop=False,
        )
        self.net.setInput(image_Blob)
        output = self.net.forward()

        H = output.shape[2]
        W = output.shape[3]

        points = []
        for i in range(0, 15):
            # 해당 신체부위 신뢰도 얻음.
            probMap = output[0, i, :, :]

            # global 최대값 찾기
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

            # 원래 이미지에 맞게 점 위치 변경
            x = (LOW_RES_WH * point[0]) / W
            y = (LOW_RES_WH * point[1]) / H

            # 키포인트 검출한 결과가 0.1보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
            if prob > 0.1:
                points.append((int(x), int(y)))
            else:
                points.append(None)

        print(points)

        for pair in self.POSE_PAIRS:
            partA = pair[0]  # Head
            partA = self.BODY_PARTS[partA]  # 0
            partB = pair[1]  # Neck
            partB = self.BODY_PARTS[partB]  # 1

            # print(partA," 와 ", partB, " 연결\n")
            if points[partA] and points[partB]:
                cv2.line(image, points[partA], points[partB], (0, 255, 0), 2)

        return image
