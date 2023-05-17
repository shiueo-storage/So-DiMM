import cv2
import mediapipe as mp
from openpyxl import Workbook
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


def convert(video_path, dev=False):
    parts_list = [
        "nose",
        "left_eye_inner",
        "left_eye",
        "left_eye_outer",
        "right_eye_inner",
        "right_eye",
        "right_eye_outer",
        "left_ear",
        "right_ear",
        "mouth_left",
        "mouth_right",
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_wrist",
        "right_wrist",
        "left_pinky",
        "right_pinky",
        "left_index",
        "right_index",
        "left_thumb",
        "right_thumb",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_heel",
        "right_heel",
        "left_foot_index",
        "right_foot_index",
    ]

    (
        list0,
        list1,
        list2,
        list3,
        list4,
        list5,
        list6,
        list7,
        list8,
        list9,
        list10,
        list11,
        list12,
        list13,
        list14,
        list15,
        list16,
        list17,
        list18,
        list19,
        list20,
        list21,
        list22,
        list23,
        list24,
        list25,
        list26,
        list27,
        list28,
        list29,
        list30,
        list31,
        list32,
    ) = (
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
    )
    u_list = [
        list0,
        list1,
        list2,
        list3,
        list4,
        list5,
        list6,
        list7,
        list8,
        list9,
        list10,
        list11,
        list12,
        list13,
        list14,
        list15,
        list16,
        list17,
        list18,
        list19,
        list20,
        list21,
        list22,
        list23,
        list24,
        list25,
        list26,
        list27,
        list28,
        list29,
        list30,
        list31,
        list32,
    ]

    print(video_path)
    exel_file = Workbook()
    exel_file_ws = exel_file.active
    for i in range(len(parts_list)):
        exel_file_ws.cell(i + 1, 1, parts_list[i])

    c_cap = 2
    cap = cv2.VideoCapture(video_path)
    with mp_pose.Pose(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            SODIMM_POINTS = results.pose_landmarks
            if SODIMM_POINTS:
                # print(SODIMM_POINTS.landmark)
                for i in range(len(SODIMM_POINTS.landmark)):
                    if SODIMM_POINTS.landmark[i].visibility > 0.2:
                        u_list[i][0].append(SODIMM_POINTS.landmark[i].x)
                        u_list[i][1].append(SODIMM_POINTS.landmark[i].y)
                    else:
                        u_list[i][0].append(0)
                        u_list[i][1].append(0)
            else:
                for i in range(33):
                    u_list[i][0].append(0)
                    u_list[i][1].append(0)

            c_cap += 1

            if dev:
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )
                # Flip the image horizontally for a selfie-view display.
                cv2.imshow("Rigging your video", cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break

    cap.release()
    cv2.destroyAllWindows()
    print(u_list)
    return u_list
