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


class JointNormal():
    def __init__(self, width, height, connect_point, vec_point):
        self.width = width
        self.height = height
        self.connect_point = connect_point
        self.vec_point = vec_point
    
    def extract_vec_norm_by_small_part(self, keypoints):
        point = list(keypoints.values())
        left_shoulder = self.connect_point[14]
        right_hip = self.connect_point[6]
        normalize_value = (point[left_shoulder][0] * self.width - point[right_hip][0] * self.width,
                           point[left_shoulder][1] * self.height - point[right_hip][1] * self.height)
     
        # 몸통에 대한 L2 normalization(일반화)
        normalize_value = np.linalg.norm(normalize_value)

        if normalize_value < 1.0:
            normalize_value = 1

        output = []

        for parts in self.vec_point.values():
            output_part = []
            p = self.connect_point[parts[0]]
            q = self.connect_point[parts[1]]
            x1, y1 = point[p][0] * self.width / normalize_value, point[p][1] * self.height / normalize_value
            x2, y2 = point[q][0] * self.width / normalize_value, point[q][1] * self.height / normalize_value
            output_part.append((x2 - x1, y2 - y1))
            output.append(output_part)
        return output  # left_leg, right_leg, left_arm, right_arm, body(nomalization)
    

class PointAccuracy():
    def __init__(self, compare_frame, before_frame, match_frame, sync_frame, keypoints):
        self.compare_frame = compare_frame
        self.before_frame = before_frame
        self.match_frame = match_frame
        self.sync_frame = sync_frame
        self.keypoints = keypoints

    def cosine_similar(self, gt, target):
        output = []
        for i in range(len(gt)):
            if np.linalg.norm(gt[i]) != 0 and np.linalg.norm(target[i]) != 0:
                c_s = np.dot(gt[i], target[i]) / (np.linalg.norm(gt[i]) * np.linalg.norm(target[i]))
                output.append(c_s)
        return np.average(output)

    def coco_oks(self, gt, target, part):
        output = []
        for i in range(len(gt)):
            gx, gy = gt[i][0], gt[i][1]
            tx, ty = target[i][0], target[i][1]
            dx = gx - tx
            dy = gy - ty
            kp_c = connect_info.sigma[connect_info.vec_part_key[part]]
            oks = np.exp(-(dx ** 2 + dy ** 2) / (2 * (kp_c ** 2)))
            output.append(oks)
        return np.average(output)
    

    def accuracy_eval(self, sc, gt):
        total_eval = [[] for _ in range(11)]
        mean_eval =[]

        s = 0
        for part in range(len(sc)):
            eval = self.coco_oks(gt[part], sc[part], part) * (self.cosine_similar(gt[part], sc[part]) / 2 + 0.5)
            total_eval[part].append(eval)
            s += eval
            total_eval[-1].append(s / len(sc))
    
        for eval in total_eval:
            mean_eval.append(np.mean(eval))
        score = np.mean(mean_eval)
        return score 
    
    # 현재 keypoint json to json 비교 코드 작성
    def video_compare(self, number):
        video_joint = JointNormal(480, 640, connect_info.info_dict, connect_info.small_parts)
        if number % self.compare_frame == 0:
            print("number!!", number)
            s_p = max(int(number * self.match_frame + self.sync_frame) - self.compare_frame, 5)
            e_p = min(int(number * self.match_frame + self.sync_frame) + self.compare_frame, 396)

            print("s_p", s_p)
            print("e_p", e_p)

            sc_joint = video_joint.extract_vec_norm_by_small_part(self.keypoints)

            total_eval = [[] for _ in range(11)]
            for j in range(s_p, e_p, 1):
                with open(os.path.join(key_path, gt_target_video, f'{j:0>4}.json')) as json_file:
                    gt_temp = json.load(json_file)
                gt_joint = video_joint.extract_vec_norm_by_small_part(gt_temp)

                score = self.accuracy_eval(sc_joint, gt_joint)
            return score
    

    def save_score_img(self, score, threshold, img):
        s = str(round(score, 3))
        if score > threshold:
            cv2.imwrite("./eval/" + s + ".png", img)    


class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID

    def camPreview(self, previewName, camID):
        cv2.namedWindow(previewName)
        cam = cv2.VideoCapture(camID)
        print(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        print(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if cam.isOpened():  # try to get the first frame
            rval, frame = cam.read()
        else:
            rval = False

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            i = 0
            sc_len = 0
            
            while rval:
                rval, frame = cam.read()
                if camID == 1:
                    image = frame
                else:
                    image = cv2.resize(frame, dsize=(480, 640), fx=1, fy=1, interpolation=cv2.INTER_LINEAR)

                image.flags.writeable = False
                image_result = pose.process(image)
                image.flags.writeable = True

                try:
                    pose_landmarks = image_result.pose_landmarks.landmark
                except:
                    i += 1
                    continue

                if self.camID == 1:
                    keypoints = config.make_keypoints(pose_landmarks, mp_pose)
                    accuracy = PointAccuracy(40, 5, 1, 5, keypoints)
                    score = accuracy.video_compare(i)

                    if score != None:
                        print("score!!!", score)
                    i += 1
                    
                mp_drawing.draw_landmarks(image, image_result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(203, 17, 17), thickness=2, circle_radius=2))

                cv2.imshow(previewName, image)
                key = cv2.waitKey(20)
                if key == 27:  # exit on ESC
                    break
            cv2.destroyWindow(previewName)
    
    def camInform(self):
        cam = cv2.VideoCapture(self.camID)
        cam_inform = {
            'frame_width': int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'frame_height': int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'video_fps': cam.get(cv2.CAP_PROP_FPS),
            'total_frame': int(cam.get(cv2.CAP_PROP_FRAME_COUNT)),
        }

        return cam_inform
    

    def run(self):
        print("Starting " + self.previewName)
        self.camPreview(self.previewName, self.camID)
     

if __name__ == "__main__":
    #with open(os.path.join(key_path, gt_target_video, f'_info.json')) as json_file:
    #    gt_inform = json.load(json_file)

    thread1 = camThread("Camera 1", 1)
    thread2 = camThread("Camera 2", os.path.join(video_path, gt_target_video))

    thread1.start()
    thread2.start()

    #process1 = multiprocessing.Process(target=thread_function, args=("Camera1", 0, gt_inform['total_frame']))
    #process2 = multiprocessing.Process(target=thread_function, args=("Camera2", os.path.join(video_path, gt_target_video), gt_inform['total_frame']))
    
    #process1.start()
    #process2.start()

    #process1.join()
    #process2.join()
    #print("finished!!")
    #thread1 = camThread("Camera 1", 0)
    #thread2 = camThread("Camera 2", os.path.join(video_path, gt_target_video))
    #thread1.start()
    #thread2.start()
