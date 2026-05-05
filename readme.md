# 🏏 AI Cricket Bowling Analyzer 🤖

A computer vision-based system that analyzes cricket fast bowling mechanics using Python and MediaPipe.  
This project processes bowling videos and generates a real-time analytics dashboard with biomechanical insights.

---

## ✨ Key Features

- 🤸 **Pose Estimation:** Detects full-body skeleton using MediaPipe (33 landmarks)
- 👤 **Head Posture Analysis:** Identifies excessive forward head movement (Head Drop)
- 🦵 **Jump & Landing Detection:** Tracks ankle movement to detect jump and landing phases
- 📐 **Joint Angle Calculation:** Computes angles like elbow and knee using vector mathematics
- 📺 **Dashboard UI:** Clean semi-transparent overlay displaying real-time metrics

---

## ⚠️ Important Note

This system **does NOT classify bowling actions as legal or illegal**.  
Due to 2D pose estimation limitations, it focuses on identifying **movement patterns and potential risks** for analysis.

---

## 🛠️ Tech Stack

- Python 3
- OpenCV (`cv2`)
- MediaPipe (`mediapipe`)
- NumPy

---

## 🚀 How It Works

1. Extracts body landmarks using MediaPipe Pose
2. Tracks motion using key points (ankle, wrist, shoulder)
3. Applies vector math to compute joint angles
4. Detects motion phases (jump, landing)
5. Displays insights using a real-time overlay dashboard

---

## 💻 Installation

```bash
git clone https://github.com/yourusername/ai-bowling-analyzer.git
cd ai-bowling-analyzer
pip install opencv-python mediapipe numpy
