import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile

# Page layout setup
st.set_page_config(page_title="AI Cricket Coach", page_icon="🏏", layout="centered")

# 📐 Angle Calculation Function
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
    return angle

# 🖥️ UI Header
st.title("🏏 The Ultimate AI Cricket Coach")
st.write("Upload a slow-motion video of a fast bowler to analyze their biomechanics in real-time.")

# 📤 Video Uploader
uploaded_file = st.file_uploader("Upload Bowling Video (MP4/AVI/MOV)", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Streamlit me OpenCV ko file path chahiye hota hai, isliye hum ek temporary file banayenge
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    st.success("Video Uploaded Successfully! Processing started... 🔥")
    
    # Ye ek khali dibba hai jisme hum live frames dalenge
    frame_window = st.image([])
    
    # AI Tools setup
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils
    
    cap = cv2.VideoCapture(tfile.name)
    
    # 🧠 AI ki Memory (State Machine)
    bowler_state = "RUNNING"
    landing_knee_angle = 0
    min_wrist_y = 9999
    release_elbow_angle = 0
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        height, width, _ = frame.shape
        
        # 🛠️ THE MAGIC FIX: Frame ko clean aur "Contiguous" banana
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # 🎯 1. HEAD DROP LOGIC
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose_y = int(nose.y * height)
            shoulder_y = int((left_shoulder.y + right_shoulder.y) / 2 * height)
            head_distance = shoulder_y - nose_y

            # 🎯 2. ANKLE TRACKING
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
            ankle_y = int(left_ankle.y * height)

            # 🎯 3. STATE MACHINE LOGIC (With Tuned 265 Threshold)
            if ankle_y < 265:
                bowler_state = "JUMPING"

            elif bowler_state == "JUMPING" and ankle_y > 330:
                bowler_state = "LANDED"

                # EXACT LANDING FRAME PAR KNEE ANGLE
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
                landing_knee_angle = calculate_angle(hip, knee, ankle)

            # 🎯 4. BALL RELEASE & CHUCKING LOGIC
            if bowler_state == "LANDED":
                right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                wrist_y = int(right_wrist.y * height)

                if wrist_y < min_wrist_y:
                    min_wrist_y = wrist_y
                    r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
                    r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y]
                    r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y]
                    release_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

            # 🎨 DRAW SKELETON
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2))

            # ==========================================
            # 🔥 PREMIUM UI DASHBOARD (Transparent Box)
            # ==========================================
            overlay = frame.copy()
            cv2.rectangle(overlay, (20, 20), (550, 260), (0, 0, 0), -1)
            alpha = 0.4
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            # ==========================================
            # ✍️ CLEAN TEXT OVERLAYS
            # ==========================================
            if head_distance < 80:
                cv2.putText(frame, f'Head: DROP ({head_distance})', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f'Head: STABLE ({head_distance})', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(frame, f'Ankle Y: {ankle_y}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f'STATE: {bowler_state}', (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 100), 2)

            if landing_knee_angle > 0:
                cv2.putText(frame, f'Knee Angle: {int(landing_knee_angle)} deg', (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
            if release_elbow_angle > 0:
                cv2.putText(frame, f'Elbow Release: {int(release_elbow_angle)} deg', (30, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 100), 2)

        # 📺 STREAMLIT LIVE VIDEO UPDATE
        # Ye line har frame ko browser me update karegi
        frame_window.image(frame, channels="BGR")
        
    cap.release()
    st.success("✅ Analysis Complete! Action Breakdown Done.")