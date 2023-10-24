import threading
import multiprocessing
import time
import cv2
import mediapipe as mp
import numpy as np
import json
import os

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
sc_video_path = path.video_path
gt_video_path = path.video_path
sc_target_video = path.sc_target_video
gt_target_video = path.gt_target_video


cap = cv2.VideoCapture(1)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
      
        if ret is False:
            break


        image = frame
           
        image.flags.writeable = False     
        results = pose.process(image)
   
        image.flags.writeable = True
  

        try:
            landmarks = results.pose_landmarks.landmark
        except:
            i = i + 1
            continue    

           
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                              landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
          

        cv2.imshow("gt", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()