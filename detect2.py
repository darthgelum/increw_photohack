from PIL import Image, ImageDraw
import json
import face_recognition
import math
image = face_recognition.load_image_file("images/me.jpg")
face_landmarks_list = face_recognition.face_landmarks(image)
print("I found {} face(s) in this photograph.".format(len(face_landmarks_list)))
pil_image = Image.fromarray(image)
d = ImageDraw.Draw(pil_image)


def calculate_top(nose_pick, nose_top, face_bottom, chin , right_eye, left_eye):
    angle = math.atan2(nose_top[1] - nose_pick[1], nose_top[0] - nose_pick[0])
    #third = math.sqrt((nose_pick[0]-face_bottom[0]) ** 2 + (nose_pick[1]-face_bottom[1])**2)
    face_width = get_distance_between_points(chin[0],chin[-1])
    third = get_distance_between_points(nose_pick, face_bottom)
    third_by_width =(face_width / 3) * 4
    # if third > ((face_width / 3) * 4):
    #     third = (face_width / 3) * 4
    # seventh = get_distance_between_points(nose_pick, face_bottom)/6
    # if third > seventh * 7:
    #     third = (seventh*7)/3
    top_npick_distance = third*2
    face_top_point = get_point_by_angle_and_distance(nose_pick, top_npick_distance, angle)
    top_circle_center = get_point_by_angle_and_distance(nose_pick, third, angle)
    top_points_left = [face_top_point]
    i = 1
    while i < 5:
        top_points_left.append(get_point_by_angle_and_distance(top_circle_center, third, angle - (math.radians(22.5) * i)))
        i += 1
    i = 1
    top_points_right =[]
    while i < 5:
        top_points_right.append(get_point_by_angle_and_distance(top_circle_center, third, angle + (math.radians(22.5) * i)))
        i += 1
    top_points_right.reverse()
    right_edge = get_distance_between_points(nose_top,chin[-1])
    left_edge = get_distance_between_points(nose_top,chin[0])
    if top_points_right[0][0] < chin[-1][0] and chin[0][0] > top_points_left[-1][0] and (right_edge > left_edge):
        difference_right = chin[-1][0] - top_points_right[0][0]
        i = 0
        while i < len(top_points_right):
            top_points_right[i] = (top_points_right[i][0] + difference_right, top_points_right[i][1])
            i += 1
        i=0
        difference_left = chin[0][0] - top_points_left[-1][0]
        while i < len(top_points_left):
            top_points_left[i] = (top_points_left[i][0]+difference_left, top_points_left[i][1])
            i += 1
    # if top_points_left[0][0] > chin[0][0] and chin[-1][0] < top_points_right[0][0] and (right_edge < left_edge):
    #     difference_left = top_points_left[0][0]-chin[0][0]
    #     i = 0
    #     while i < len(top_points_left):
    #         top_points_left[i] = (top_points_left[i][0] - difference_left, top_points_left[i][1])
    #         i += 1
    #     i=0
    #     difference_right = top_points_right[-1][0] - chin[-1][0]
    #     while i < len(top_points_right):
    #         top_points_right[i] = (top_points_right[i][0]-difference_left, top_points_right[i][1])
    #         i += 1
    return {"left": top_points_left, "right": top_points_right}


def get_point_by_angle_and_distance(point, distance, angle):
    return point[0] + distance * math.cos(angle), point[1] + distance * math.sin(angle)


def get_distance_between_points(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


face = face_landmarks_list[0]
nose_bridge = face["nose_bridge"]
nose_tip = face["nose_tip"]
chin = face["chin"]
right_eye = face["right_eye"]
left_eye = face["left_eye"]
nose_pick = nose_bridge[3]
nose_bottom = nose_tip[2]
nose_top = nose_bridge[0]
face_bottom = chin[8]

top_points = calculate_top(nose_pick, nose_top, face_bottom, chin, right_eye, left_eye)
face["chin"] = top_points["left"] + face["chin"] + top_points["right"]

for facial_feature in face.keys():
    d.line(face[facial_feature], width=5)
d.line([face["chin"][0], face["chin"][25]], width=5)
pil_image.show()

print(json.dumps(face))
