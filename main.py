import cv2
import mediapipe as mp
import json

def extract_keypoints_from_video(video_path, output_path):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(video_path)
    keypoints_data = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            if results.pose_landmarks:
                keypoints = []
                for landmark in results.pose_landmarks.landmark:
                    keypoints.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })
                keypoints_data.append(keypoints)

    with open(output_path, 'w') as outfile:
        json.dump(keypoints_data, outfile)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = "input_video.mp4"
    output_path = "keypoints_data.json"
    extract_keypoints_from_video(video_path, output_path)