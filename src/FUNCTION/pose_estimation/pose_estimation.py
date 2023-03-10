import cv2
from PIL import Image

from utils import global_path


class Pose_Estimator:
    def __init__(self):
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

        self.protoFile = global_path.get_proj_abs_path("assets/models/pose_deploy_linevec.prototxt")
        self.weightsFile = global_path.get_proj_abs_path("assets/models/pose_iter_440000.caffemodel")

        self.net = cv2.dnn.readNetFromCaffe(self.protoFile, self.weightsFile)
        print("model loaded")

    def video_estimate(self, video):
        cap = cv2.VideoCapture(video)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        frame_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(frame_num, fps)

        out = cv2.VideoWriter(global_path.get_proj_abs_path("assets/test/test_out.mp4"), fourcc, fps, (256,256))

        frame_count = 0
        while cap.isOpened():
            (ret, frame) = cap.read()
            frame_count+=1
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = self.image_estimate(frame)
                cv2.imshow("asdasd",frame)
                cv2.waitKey(10)
                out.write(frame)
                print(f"FRAME: {frame_count} / {frame_num}")
            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print('done')

    def image_estimate(self, image):
        image = cv2.resize(image, (256,256))
        image_Blob = cv2.dnn.blobFromImage(image, 1.0 / 255, (256, 256), (0, 0, 0), swapRB=False, crop=False)
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
            x = (256 * point[0]) / W
            y = (256 * point[1]) / H

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