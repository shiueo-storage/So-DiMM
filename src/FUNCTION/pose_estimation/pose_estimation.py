import cv2

from utils import global_path

BODY_PARTS = {
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

POSE_PAIRS = [
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


class POSE_ESTIMATOR:
    def __init__(self):
        super(POSE_ESTIMATOR, self).__init__()

        protoFile = global_path.get_proj_abs_path("assets/models/pose_deploy_linevec.prototxt")
        weightsFile = global_path.get_proj_abs_path("assets/models/pose_iter_440000.caffemodel")

        self.NET = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
        print("POSE_ESTIMATION - LOADED")

    def get_pose(self, img_path):
        img = cv2.imread(img_path)
        imageHeight, imageWidth, _ = img.shape

        imgBlob = cv2.dnn.blobFromImage(
            img, 1.0 / 255, (imageWidth, imageHeight), (0, 0, 0), swapRB=False, crop=False
        )

        self.NET.setInput(imgBlob)

        output = self.NET.forward()

        H = output.shape[2]
        W = output.shape[3]



