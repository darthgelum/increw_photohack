from PIL import Image, ImageDraw
import json
import face_recognition
import math
import os
from flask import Flask, render_template, request, flash, url_for
from werkzeug.utils import redirect, secure_filename

UPLOAD_FOLDER = './images/web'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






def calculate_top(nose_pick, nose_top, face_bottom, chin , right_eye, left_eye):
    angle = math.atan2(nose_top[1] - nose_pick[1], nose_top[0] - nose_pick[0])
    #third = math.sqrt((nose_pick[0]-face_bottom[0]) ** 2 + (nose_pick[1]-face_bottom[1])**2)
    face_width = get_distance_between_points(chin[0], chin[-1])
    face_height = (((face_width/3)*4)/6)*8
    third = get_distance_between_points(right_eye[3], left_eye[3])
    third = (((third*3)/6)*8)/3
    # third_by_width =(face_width / 3) * 4
    # #if third > third_by_width:
    # third = third_by_width
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
    width_percent = face_width/100
    edge_difference = right_edge-left_edge
    diff_coeff = edge_difference/width_percent
    percent_to_correct = 15
    if top_points_right[0][0] < chin[-1][0] and chin[0][0] > top_points_left[-1][0] and (diff_coeff>0 and diff_coeff>percent_to_correct):
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
    if top_points_left[4][0] > chin[0][0] and chin[-1][0] < top_points_right[0][0] and (diff_coeff<0 and diff_coeff<-percent_to_correct):
        difference_left = top_points_left[4][0]-chin[0][0]
        i = 0
        while i < len(top_points_left):
            top_points_left[i] = (top_points_left[i][0] - difference_left, top_points_left[i][1])
            i += 1
        i=0
        difference_right = top_points_right[0][0] - chin[-1][0]
        while i < len(top_points_right):
            top_points_right[i] = (top_points_right[i][0]-difference_right, top_points_right[i][1])
            i += 1
    return {"left": top_points_left, "right": top_points_right}


def get_point_by_angle_and_distance(point, distance, angle):
    return point[0] + distance * math.cos(angle), point[1] + distance * math.sin(angle)


def get_distance_between_points(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            image = face_recognition.load_image_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            face_landmarks_list = face_recognition.face_landmarks(image)

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

            # for facial_feature in face.keys():
            #     d.line(face[facial_feature], width=5)
            # d.line([face["chin"][0], face["chin"][25]], width=5)
            # pil_image.show()

            #print(json.dumps(face))

            return json.dumps(face)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


app.debug = True
app.run(host='0.0.0.0', port=5000)


