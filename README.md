# DJI Tello Face Following

This project implements a face detection and tracking system for the DJI Tello drone. It can also work with a regular webcam for testing purposes. The system uses OpenCV's Haar Cascade classifier for face detection and controls the drone to autonomously follow the largest detected face by adjusting its position in 3D space.

## 🚀 Features

* Face detection and tracking using the Tello drone's camera or a webcam
* Autonomous drone control to keep the detected face centered in the frame
* Manual takeoff/landing controls via keyboard
* Option to display the video feed with tracking visualization
* Option to save the video feed to a file for later analysis

## ▶️ Demo
[![Video Title](https://img.youtube.com/vi/ZMhzxzPc_Zs/0.jpg)](https://www.youtube.com/watch?v=ZMhzxzPc_Zs) 

## 🛠️ Installation

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/2black0/DJI-Tello-Face-Following.git
cd tello-face-following
```

### 2. Create a Virtual Environment (Optional but Recommended)

To create and activate a virtual environment (optional but recommended):

```bash
conda create --name tello-face-following-env python=3.11
conda activate tello-face-following-env
```

Alternatively, use `virtualenv` or any Python environment manager of your choice.

### 3. Install Dependencies

Install all the required dependencies from the `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Haar Cascade Classifier File

Ensure the `haarcascade_frontalface_default.xml` file is in the same directory as the `tello-face-following.py` script. This file is used for face detection.

---

## 📂 Project Structure

```
.
├── LICENSE                            # Project license
├── Project
│   ├── haarcascade_frontalface_default.xml  # Haar cascade file for face detection
│   ├── other                           # Other files or resources (if any)
│   ├── requirements.txt               # List of dependencies
│   └── tello-face-following.py        # Main face tracking script
└── README.md                          # Project documentation
```

---

## 💻 Usage

### 1. Running the Script

To start the face tracking system with the Tello drone or a webcam, run the following command:

```bash
python tello-face-following.py [--tello] [--webcam INDEX] [--resolution WIDTH HEIGHT] [--show] [--save]
```

* **`--tello`**: Use the DJI Tello drone for face tracking (without this flag, the webcam is used by default).
* **`--webcam INDEX`**: Specify the webcam index if using a webcam (default is `0`).
* **`--resolution WIDTH HEIGHT`**: Set the resolution for the video feed (default is `640 480`).
* **`--show`**: Display the video feed with face tracking visualization.
* **`--save`**: Save the video feed to a file (`tracking.avi`).

### 2. Manual Drone Control

While the script is running:

* Press **T** to take off.
* Press **L** to land.
* Press **Q** to exit the program.

### 3. Visual Feedback

* The video feed will display the detected face with a bounding box and a center point.
* A line will be drawn from the frame center to the face center, showing the drone's adjustment direction.
* If the **`--show`** flag is enabled, the live video feed will be shown.
* If the **`--save`** flag is enabled, the video feed will be saved to a file.

### 4. Error Handling

The script uses basic error handling to ensure smooth operation. If the face is not detected, the drone will not move. If the face is too close or too far, the system will adjust the drone's position to maintain a comfortable distance.

---

## 🔧 Dependencies

* **OpenCV**: For face detection and video handling (`cv2`).
* **djitellopy**: Python library to control the DJI Tello drone.
* **pygame**: For handling keyboard input for manual control.
* **numpy**: For numerical calculations and array manipulations.

These dependencies are listed in the `requirements.txt` file and can be installed via:

```bash
pip install -r requirements.txt
```

---

## 🔐 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---
