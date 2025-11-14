# 🚁 Drone Landing Check System (Polarization Test)

This project provides a Python-based Graphical User Interface (GUI) application to perform an automated landability check for a drone by detecting highly reflective surfaces (like mirrors or glare from water) using a controlled polarized filter.

It includes an offline test version of the main script (`final_cam_gui.py`) and a utility script (`camera_test.py`) for hardware setup.

## ⚠️ Important Note: Test Mode
This version (`final_cam_gui.py`) runs in **TEST MODE**. It simulates drone mode changes (`LAND` or `LOITER`) but does not communicate with a real Pixhawk or flight controller.

---

## 🛠️ Project Setup and Dependencies

### Recommended: Use a Python Virtual Environment 🧪

It is **highly recommended** to use a Python virtual environment (like `venv`) to manage the project's dependencies. This prevents conflicts with other Python projects on your system.

**1. Create the Environment:**
```bash
# Using venv (standard Python module)
python -m venv venv
