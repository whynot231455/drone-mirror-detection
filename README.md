# 🚁 Drone Landing Check System (Polarization Test)

<img width="1280" height="640" alt="github_drone-landing" src="https://github.com/user-attachments/assets/d37765df-ac0a-4566-8886-abbcaf8f2bd2" /> </p>

## Circuit Diagram
<img width="1280" height="640" alt="github_circuit-diagram" src="https://github.com/user-attachments/assets/fc618d38-0fd5-453f-a34a-2888f710015b" /> </p>

A Python-based **Graphical User Interface (GUI)** application designed to perform an automated **drone landability check** by detecting **highly reflective surfaces** such as mirrors, glass, or water glare using a **polarized filter system**.

This project includes:

- `final_cam_gui.py` — Main GUI application (**TEST MODE**)
- `camera_test.py` — Utility script to find the correct camera index

---

## ⚠️ Test Mode Notice

The main script runs in **TEST MODE**, meaning:

- Drone mode changes (`LAND`, `LOITER`) are **simulated**
- No communication occurs with a real Pixhawk or flight controller

This mode is ideal for offline testing and UI validation without hardware risk.

---

## 🛠️ Project Setup & Dependencies

### 🔹Create a Virtual Environment (Highly Recommended)

This prevents package conflicts and keeps your environment clean.

```bash
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Install required libraries
pip install opencv-python pyserial numpy pillow

```
## ⚙️ Hardware & Configuration

### 🔸 1. Camera Index Setup (Extremely Important)

Run the camera testing utility:
```bash
python camera_test.py
```
Check each index and locate the one showing the actual drone camera feed.

Then update the value in final_cam_gui.py:

```bash
CAMERA_INDEX = <your_camera_index> //line 16 (in final_cam_gui.py)
```

### 🔸 2. Servo / Arduino Configuration

The system uses serial communication to rotate a servo-mounted polarizer.

Ensure that:
- Your Arduino is connected
- The COM port is correctly set
  
Modify the port inside final_cam_gui.py if required:
```bash
SERVO_PORT = "COM6"   # Replace with your Arduino COM port
```
## ▶️ Running the Main Application

Make sure the virtual environment is active, then run:
```bash
python final_cam_gui.py
```
This starts the GUI, live camera feed, and the polarization-based landing evaluation system.

## 📁 Included Scripts

| File               | Description                              |
| ------------------ | ---------------------------------------- |
| `final_cam_gui.py` | Main GUI application (TEST MODE)         |
| `camera_test.py`   | Script to determine correct camera index |
