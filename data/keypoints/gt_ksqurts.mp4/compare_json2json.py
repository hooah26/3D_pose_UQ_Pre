import time
import cv2
import mediapipe as mp
import numpy as np
import json
import os
import config
import vector_normal
import path
import connect_info
import video_info

pTime = 0
sTime = time.time()
# mediapipe 설정
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


if __name__=="__main__":
    
    gt_cap = cv2.VideoCapture(os.path.join(video_path, gt_target_video))
    #sc_cap = cv2.VideoCapture(os.path.join(video_path, sc_target_video))
    sc_cap = cv2.VideoCapture(0)

    gt_video_info = video_info.VideoInfo(key_path, video_path, gt_target_video, gt_cap)
    sc_video_info = video_info.VideoInfo(key_path, video_path, sc_target_video, sc_cap)

    gt_inform = gt_video_info.load_video_info_json()
    sc_inform = sc_video_info.load_video_info_json()

    # gt와 비교할 Frame 수 선정
    compare_frame = 20
    before_frame = 5
    match_frame = gt_inform['video_fps'] / sc_inform['video_fps']  # 비디오 두 프레임이 다를 경우에 Sync를 맞춰줌
    sync_frame = 5
    
    gt_video = vector_normal.VecNormal(gt_inform['frame_width'], gt_inform['frame_height'])
    prac_video = vector_normal.VecNormal(sc_inform['frame_width'], sc_inform['frame_height'])
    compare_video = vector_normal.PointAccuracy(compare_frame, before_frame, match_frame, sync_frame)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        i = 0
        while sc_cap.isOpened():
            gt_ret, gt_frame = gt_cap.read()
            sc_ret, sc_frame = sc_cap.read()

            if sc_ret is False:
                print("RET IS False GT RET")
                break
            if i >= sc_inform['total_frame'] - 1:
                break

            gt_image = gt_video_info.resize_video(gt_frame, 480, 640)
            sc_image = sc_video_info.resize_video(sc_frame, 480, 640)

            gt_image.flags.writeable = False
            gt_results = pose.process(gt_image)
            gt_image.flags.writeable = True

            sc_image.flags.writeable = False
            sc_results = pose.process(sc_image)
            sc_image.flags.writeable = True

            try:
                gt_landmarks = gt_results.pose_landmarks.landmark
                sc_landmarks = sc_results.pose_landmarks.landmark

            except:
                i = i + 1
                continue

            sc_keypoints = config.make_keypoints(sc_landmarks, mp_pose)
            gt_keypoints = config.make_keypoints(gt_landmarks, mp_pose)
            gt_video_info.visualization(gt_image, gt_results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 0, 0, 0, 203, 17, 17, 2, 2, 2, 2)
            sc_video_info.visualization(sc_image, sc_results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 0, 0, 0, 203, 17, 17, 2, 2, 2, 2)

            
            if i % (compare_frame) == 0:
                s_p = max(int(i * match_frame + sync_frame) - compare_frame, 5)  # start point
                e_p = min(int(i * match_frame + sync_frame) + compare_frame, gt_inform['total_frame'] - 1)  # end point
    
                # body part별로(왼다리, 오른다리, 왼팔, 오른팔, 몸통) normalize된 값 vector 추출
                sc = prac_video.extract_vec_norm_by_small_part(sc_keypoints)

                total_eval = [[] for _ in range(11)]

                for j in range(s_p, e_p, 1):
                    gt_temp = gt_video_info.keypoint_load_json(j)
                    gt = gt_video.extract_vec_norm_by_small_part(gt_temp)
                    score = compare_video.Accuracy_eval(sc, gt)
                print(score)

            i = i + 1
            img = cv2.hconcat([gt_image, sc_image])
            #compare_video.save_score_img(score, 0.80, img)

            cv2.imshow("compare", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        gt_cap.release()
        sc_cap.release()
        cv2.destroyAllWindows()