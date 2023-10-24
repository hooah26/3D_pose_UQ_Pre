import cv2
import mediapipe as mp
import numpy as np
import json
import time
import os
import argparse
import math

from utility import config
from utility import path
from utility import connect_info

pTime = 0
sTime = time.time()
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic
mp_drawing_styles = mp.solutions.drawing_styles


key_path = path.key_path
video_path = path.video_path
gt_target_path = path.gt_target_video
sc_target_path = path.sc_target_video
gt_img_path = path.gt_img_path
sc_img_path = path.sc_img_path


def human_pose_detection(cap, video, video_inform):
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        total_frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if ret is False:
                break

            frame_time = cap.get(cv2.CAP_PROP_POS_MSEC)
            resize_frame = video.resize_video(frame, 480, 640)
            image = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)

            cv2.imwrite(sc_img_path + f'{total_frame_count:0>4}.png', image)

            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
            except:
                continue

            video.save_keypoint_info_json(landmarks, mp_pose, total_frame_count)
            boxx, boxy, boxx1, boxy1 = video.gt_box_normalization(landmarks, mp_pose)
            video_inform['gt_bbox'] = [boxx, boxy, boxx1, boxy1]
            video.save_video_info_json(video_inform)

            total_frame_count += 1
            result = video.visualization(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 0, 0, 0, 203, 17, 17, 2, 2, 2, 2)
            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__=="__main__":
    os.makedirs(os.path.join(key_path, gt_target_path), exist_ok=True)
    cap = cv2.VideoCapture(os.path.join(video_path, gt_target_path))
    video = video_info.VideoInfo(key_path, video_path, gt_target_path, cap)
    video_inform = video.video_inform()
    video.save_video_info_json(video_inform)
    human_pose_detection(cap, video, video_inform)


