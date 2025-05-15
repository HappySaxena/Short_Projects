import cv2
import mediapipe as mp
import pyautogui
import time

cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
nose_tip_index = 1  

ref_x, ref_y = None, None

last_action_time = 0
cooldown_period = 0.5

while True:
    current_time = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Camera not opened")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        h, w, _ = frame.shape

        
        landmark_points = []
        for lm in face_landmarks.landmark:
            x, y = int(lm.x * w), int(lm.y * h)
            landmark_points.append((x, y))

       
        x_min, y_min = min(landmark_points, key=lambda p: p[0])[0], min(landmark_points, key=lambda p: p[1])[1]
        x_max, y_max = max(landmark_points, key=lambda p: p[0])[0], max(landmark_points, key=lambda p: p[1])[1]
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

       
        nose = face_landmarks.landmark[nose_tip_index]
        nose_x = int(nose.x * w)
        nose_y = int(nose.y * h)

        if ref_x is None:
            ref_x = nose_x
            ref_y = nose_y

        dx = nose_x - ref_x
        dy = nose_y - ref_y
        threshold = 50
        uthresold = 30

        if dx < -threshold and current_time - last_action_time > cooldown_period:
            print("Move left")
            pyautogui.press('right')
            last_action_time = current_time
        elif dx > threshold and current_time - last_action_time > cooldown_period:
            print("Move right")
            pyautogui.press('left')
            last_action_time = current_time
        elif dy <-uthresold and current_time - last_action_time > cooldown_period:
            print("Move up")
            pyautogui.press('up')
            last_action_time = current_time
        elif dy > threshold and current_time - last_action_time > cooldown_period:
            print("Move down")
            pyautogui.press('down')
            last_action_time = current_time

        
        cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)
        cv2.circle(frame, (ref_x, ref_y), 5, (0, 0, 255), -1)

    cv2.imshow("Face Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
