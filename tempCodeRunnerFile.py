import cv2
import numpy as np
from deepface import DeepFace
import mediapipe as mp

mp_mesh = mp.solutions.face_mesh
face_mesh = mp_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

LEFT = [33,160,158,133,153,144]
RIGHT = [263,387,385,362,380,373]

def EAR(land, idx, w, h):
    pts = [(int(land[i].x*w), int(land[i].y*h)) for i in idx]
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    if C == 0:
        return 1
    return (A+B)/(2*C)

def analyze_emotion(frame):
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = {
        "dominant": "neutral",
        "sleep_alert": False
    }

    face = face_mesh.process(rgb)

    if face.multi_face_landmarks:
        land = face.multi_face_landmarks[0].landmark

        # Sleep detection
        earL = EAR(land, LEFT, w, h)
        earR = EAR(land, RIGHT, w, h)
        ear_avg = (earL + earR) / 2
        
        if ear_avg < 0.21:
            result["sleep_alert"] = True

        # Emotion detection
        try:
            emo = DeepFace.analyze(rgb, actions=["emotion"], enforce_detection=False)
            result["dominant"] = emo["dominant_emotion"]
        except:
            result["dominant"] = "neutral"

    return result
