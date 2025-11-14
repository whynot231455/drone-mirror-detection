# updated_gui_mirror_landbutton_showcaptures_nopixhawk.py
# GUI + Polarizer capture + Automatic servo move + Decision logic
# Live brightness + Show Before & After captured ROI images
# OFFLINE TEST VERSION (No Pixhawk Required)

import cv2
import serial
import time
import numpy as np
import threading
import queue
from tkinter import Tk, Label, Button, StringVar, Frame, BOTH, X, Y, LEFT, TOP, RIGHT
from PIL import Image, ImageTk

# ======= CONFIG =======
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

POLARIZER_OFF_ANGLE = 90
POLARIZER_ON_ANGLE = 150
BRIGHTNESS_DIFF_THRESHOLD = 0.12  # decision threshold

SERVO_PORT = 'COM6'
BAUD_RATE = 9600

# ===== Arduino (servo) connection - mock fallback =====
try:
    arduino = serial.Serial(SERVO_PORT, BAUD_RATE, timeout=2)
    time.sleep(2)
    print(f"Connected to Arduino on {SERVO_PORT}")
except Exception as e:
    print(f"Could not open serial port {SERVO_PORT}: {e}. Using mock object.")
    class MockArduino:
        def write(self, data): pass
        def close(self): pass
    arduino = MockArduino()

# ===== Mock Vehicle (for testing without Pixhawk) =====
class MockVehicle:
    def __init__(self): self.mode = "MANUAL"
    def set_mode(self, new_mode):
        print(f"[MOCK PIXHAWK] Mode changed to {new_mode}")
        self.mode = new_mode

vehicle = MockVehicle()
print("Running in TEST MODE (no Pixhawk connection).")

# =======================================================

# ===== GUI setup =====
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print(f"FATAL ERROR: Could not open camera with index {CAMERA_INDEX}.")
    exit()
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

frame_queue = queue.Queue(maxsize=1)
root = Tk()
root.title('Drone Land Check (Test Mode)')
root.resizable(False, False)

main_container = Frame(root)
main_container.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=10)

# --- Left frame: live video ---
left_frame = Frame(main_container)
left_frame.pack(side=LEFT, fill=Y, padx=(0, 10))

frame_label = Label(left_frame)
frame_label.pack(side=TOP, padx=10, pady=(10, 5))

ctrl_panel = Frame(left_frame)
ctrl_panel.pack(side=TOP, fill=X, padx=10, pady=(5, 10))

brightness_var = StringVar(value="Center Brightness: N/A")
brightness_label = Label(ctrl_panel, textvariable=brightness_var, font=('Arial', 14))
brightness_label.pack(pady=(0,10))

decision_var = StringVar(value="Decision: N/A")
decision_label = Label(ctrl_panel, textvariable=decision_var, font=('Arial', 14, "bold"))
decision_label.pack(pady=(10,10))

land_btn = Button(ctrl_panel, text="Land", font=('Arial', 12, 'bold'))
land_btn.pack(pady=10, fill=X)

quit_btn = Button(ctrl_panel, text="Quit")
quit_btn.pack(pady=10, fill=X)

# --- Right frame: captured Before/After images ---
right_frame = Frame(main_container)
right_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))

before_label = Label(right_frame, text="Before (OFF)", font=('Arial', 12))
before_label.pack(pady=(10,0))
before_img_label = Label(right_frame)
before_img_label.pack(pady=(0,10))

after_label = Label(right_frame, text="After (ON)", font=('Arial', 12))
after_label.pack(pady=(10,0))
after_img_label = Label(right_frame)
after_img_label.pack(pady=(0,10))

# ===== helper functions =====
def set_servo(angle):
    """Send servo angle command to Arduino (0-180)."""
    try:
        angle_int = max(0, min(180, int(angle)))
        arduino.write(f"{angle_int}\n".encode())
    except: pass

def get_center_crop(frame, center_ratio=0.5):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    crop_w = int(w * center_ratio)
    crop_h = int(h * center_ratio)
    cx, cy = w // 2, h // 2
    left = max(0, cx - crop_w // 2)
    top = max(0, cy - crop_h // 2)
    return frame[top:top + crop_h, left:left + crop_w], (left, top, crop_w, crop_h)

def get_shiny_fraction(frame, bright_thresh=200):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if gray.size == 0: return 0.0
    _, thresh = cv2.threshold(gray, bright_thresh, 255, cv2.THRESH_BINARY)
    shiny_pixels = np.count_nonzero(thresh)
    total = gray.size
    return shiny_pixels / float(total)

def update_image_panel(panel, frame, size=(200,150)):
    resized_frame = cv2.resize(frame, size)
    rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    panel.imgtk = imgtk
    panel.config(image=imgtk)

# ===== Land check logic (Reversed for Mirror Landing) =====
def run_land_check():
    try:
        # 1. Capture with polarizer OFF (Reference)
        set_servo(POLARIZER_OFF_ANGLE)
        time.sleep(0.4)
        ret, frame_before = cap.read()
        crop_before, _ = get_center_crop(frame_before)
        bright_before = get_shiny_fraction(crop_before)
        update_image_panel(before_img_label, crop_before)

        # 2. Capture with polarizer ON (Glare Test)
        set_servo(POLARIZER_ON_ANGLE)
        time.sleep(0.4)
        ret, frame_after = cap.read()
        crop_after, _ = get_center_crop(frame_after)
        bright_after = get_shiny_fraction(crop_after)
        update_image_panel(after_img_label, crop_after)

        diff = abs(bright_before - bright_after)
        print(f"Before={bright_before:.3f}, After={bright_after:.3f}, Diff={diff:.3f}")

        # 3. Decision Logic (No Pixhawk)
        if diff > BRIGHTNESS_DIFF_THRESHOLD:
            decision_var.set("Decision: MIRROR DETECTED (SAFE TO LAND)")
            decision_label.config(fg="green")
            vehicle.set_mode("LAND")
        else:
            decision_var.set("Decision: WATER/MATTE DETECTED (DO NOT LAND)")
            decision_label.config(fg="red")
            vehicle.set_mode("LOITER")

    except Exception as e:
        print("Error in land check logic:", e)
        decision_var.set("Decision: ERROR")
        decision_label.config(fg="red")
        vehicle.set_mode("RTL")

# ===== video loop =====
running = True
def video_loop():
    while running:
        ret, frame = cap.read()
        if not ret: continue
        crop, (left, top, crop_w, crop_h) = get_center_crop(frame, center_ratio=0.5)
        cv2.rectangle(frame, (left, top), (left + crop_w, top + crop_h), (0, 255, 0), 2)
        mean_brightness = get_shiny_fraction(crop)
        brightness_var.set(f"Center Brightness: {mean_brightness:.3f}")
        if not frame_queue.full():
            try: frame_queue.get_nowait()
            except queue.Empty: pass
            frame_queue.put(frame)
        time.sleep(0.03)

def gui_update():
    try:
        if not frame_queue.empty():
            frame = frame_queue.get()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            frame_label.imgtk = imgtk
            frame_label.config(image=imgtk)
    except: pass
    if running: root.after(50, gui_update)

# ===== quit =====
def quit_app():
    global running
    running = False
    try: cap.release()
    except: pass
    try: arduino.close()
    except: pass
    root.destroy()

# Bind buttons
land_btn.config(command=lambda: threading.Thread(target=run_land_check, daemon=True).start())
quit_btn.config(command=quit_app)

# Start threads
video_thread = threading.Thread(target=video_loop, daemon=True)
video_thread.start()
root.after(0, gui_update)
root.mainloop()
