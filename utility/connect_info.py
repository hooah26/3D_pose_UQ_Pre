info_dict = {1: 0,  # left_hip
             2: 1,  # left_knee
             3: 2,  # left_ankle
             6: 3,  # right_hip
             7: 4,  # right_knee
             8: 5,  # right_ankle
             14: 6,  # left_shoulder
             15: 7,  # left_elbow
             16: 8,  # left_wrist
             19: 9,  # right_shoulder
             20: 10,  # right_elbow
             21: 11,  # right_wrist
             24: 12,  # nose
             25: 13,  # left_eye
             26: 14,  # right_eye
             27: 15,  # left_ear
             28: 16}  # right_ear


connect_point = [[1, 2, 3],  # 왼쪽다리
                 [6, 7, 8],  # 오른쪽다리
                 [14, 15, 16],  # 왼쪽팔
                 [19, 20, 21],  # 오른쪽팔
                 [1, 6, 19, 14, 1],  # 몸통
                 [28, 26, 24, 25, 27]]  # 눈코입


connect_point_parts = [[1, 2],  # left thigh
                       [2, 3],  # left calf
                       [6, 7],  # right thigh
                       [7, 8],  # right calf
                       [14, 15],  # left arm
                       [15, 16],  # left forearm
                       [19, 20],  # right arm
                       [20, 21],  # right forearm
                       [1, 6, 19, 14, 1],  # body
                       [28, 26, 24, 25, 27]]  # face


vec_point = [[1, 2], [2, 3],  # 왼쪽다리
             [6, 7], [7, 8],  # 오른쪽다리
             [14, 15], [15, 16],  # 왼쪽팔
             [19, 20], [20, 21],  # 오른쪽팔
             [24, 25], [24, 26], [24, 27], [24, 28],  # 눈코입
             [6, 14], [1, 19]]  # 몸통


vec_part = {'left_leg': [[1, 2], [2, 3]],  # 왼쪽다리
            'right_leg': [[6, 7], [7, 8]],  # 오른쪽다리
            'left_arm': [[14, 15], [15, 16]],  # 왼쪽팔
            'right_arm': [[19, 20], [20, 21]],  # 오른쪽팔
            'body': [[6, 14], [1, 19]]}  # 몸통


small_parts = {
    "left thigh": [1, 2],
    "left calf": [2, 3],
    "right thigh": [6, 7],
    "right calf": [7, 8],
    "left arm": [14, 15],
    "left forearm": [15, 16],
    "right arm": [19, 20],
    "right forearm": [20, 21],
    "body1": [6, 14],
    "body2": [1, 19]}


vec_part_key = ['left thigh',
                'left calf',
                'right thigh',
                'right calf',
                'left arm',
                'left forearm',
                'right arm',
                'right forearm',
                'body1',
                'body2']

sigma = {
    'left thigh': 0.8,  # 0.087, [1,3,5,7] #0.8 왼쪽 허벅지
    'left calf': 0.8,  # 0.089,            #0.9 왼쪽 종아리
    'right thigh': 0.8,  # 0.087,          #0.8 오른쪽 허벅지
    'right calf': 0.8,  # 0.089,           #0.9 오른쪽 종아리
    'left arm': 0.8,  # 0.072,             #0.8 왼쪽 팔
    'left forearm': 0.8,  # 0.1, #0.062    #0.9 왼쪽 팔뚝
    'right arm': 0.8,  # 0.072,            #0.8 오른쪽 팔
    'right forearm': 0.8,  # 0.1, #0.062   #0.9 오른쪽 팔뚝
    'body1': 0.8,  # 0.079,                #0.8 왼쪽 몸통
    'body2': 0.8  # 0.079                  #0.8 오른쪽 몸통
}