"""
Tello Drone Face Tracking System

This module implements a face detection and tracking system for the DJI Tello drone.
It can also work with a regular webcam for testing purposes. The system detects faces
using OpenCV's Haar cascade classifier and controls the drone to follow the largest 
detected face by adjusting its position in 3D space.

Features:
- Face detection and tracking with the Tello drone camera or webcam
- Autonomous drone control to keep the face centered in the frame
- Manual takeoff/landing controls via keyboard
- Option to display the video feed with tracking visualization
- Option to save the video feed to a file

Usage:
    python tello-face-following.py [--tello] [--webcam INDEX] [--resolution WIDTH HEIGHT] [--show] [--save]

Dependencies:
    - OpenCV (cv2)
    - djitellopy
    - pygame
    - numpy
    - haarcascade_frontalface_default.xml file in the same directory
"""
import cv2
from djitellopy import Tello
import argparse
import pygame
import sys
import logging
import os
import time

# Initialize face cascade classifier with cross-platform path handling
face_cascade_path = os.path.join('haarcascade_frontalface_default.xml')
if not os.path.exists(face_cascade_path):
    raise FileNotFoundError(f"Haar cascade file not found at {face_cascade_path}")
face_cascade = cv2.CascadeClassifier(face_cascade_path)

# Drone control parameters
ERROR_THRESHOLD = 2       # Minimum error to trigger movement
TARGET_SIZE = 40          # Target face size in pixels (for distance control)
SPEED_LIMIT = 50          # Max speed percentage (0-100)

# Initialize Pygame for keyboard input handling
pygame.init()
pygame.display.set_mode((1, 1))  # Minimal hidden window for headless compatibility

def calculate_error(frame_center, face_center, face_size):
    """
    Calculate normalized tracking errors with safety checks.
    
    Args:
        frame_center (tuple): Center coordinates of the frame (x, y)
        face_center (tuple): Center coordinates of the detected face (x, y)
        face_size (int): Height of the detected face in pixels
        
    Returns:
        list: Normalized error values [-1, 1] for x, y, and z axes
            - x: horizontal error (negative = face left of center)
            - y: vertical error (negative = face above center)
            - z: distance error (negative = face too close)
    """
    try:
        # Calculate normalized errors for each axis
        error_x = (face_center[0] - frame_center[0]) / frame_center[0]
        error_y = (face_center[1] - frame_center[1]) / frame_center[1]
        error_z = (TARGET_SIZE - face_size) / TARGET_SIZE
    except ZeroDivisionError:
        return [0, 0, 0]
    
    # Clamp errors between -1 and 1 for safety
    return [
        max(min(error_x, 1), -1),
        max(min(error_y, 1), -1),
        max(min(error_z, 1), -1)
    ]

def process_frame(img, frame_size, show_osd, show_box):
    """
    Process video frame for face detection and calculate control velocities.
    
    Args:
        img (numpy.ndarray): Input video frame
        frame_size (list): Frame dimensions [width, height]
        show_osd (bool): Whether to display on-screen information
        show_box (bool): Whether to draw tracking visualization
        
    Returns:
        list: Control velocities [left/right, forward/backward, up/down, yaw]
    """
    velocities = [0, 0, 0, 0]  # Default to no movement
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,        # How much the image size is reduced at each scale
        minNeighbors=5,         # Higher value = fewer detections but higher quality
        minSize=(30, 30),       # Minimum face size to detect
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    if len(faces) > 0:
        # Track the largest face (assumes it's the closest/most important)
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        frame_center = (frame_size[0]//2, frame_size[1]//2)
        face_center = (x + w//2, y + h//2)
        
        # Calculate position errors
        errors = calculate_error(frame_center, face_center, h)
        
        # Map errors to drone velocities (simple proportional control)
        # A PID controller would provide better stability
        velocities = [
            int(-errors[0] * SPEED_LIMIT),  # Left/Right velocity
            int(errors[2] * SPEED_LIMIT),   # Forward/Backward velocity
            int(-errors[1] * SPEED_LIMIT),  # Up/Down velocity
            int(errors[0] * SPEED_LIMIT)    # Yaw velocity (rotation)
        ]

        # Draw tracking visualization if enabled
        if show_box:
            # Draw face bounding box
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255), 2)
            # Draw face center point
            cv2.circle(img, face_center, 5, (0, 0, 255), -1)
            # Draw line from center to face
            cv2.line(img, frame_center, face_center, (255, 0, 0), 2)

    # Add on-screen display text if enabled
    if show_osd:
        cv2.putText(img, "Face Tracking Active", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return velocities

def main():
    """
    Main application entry point. Parses command line arguments, initializes
    the drone or webcam, and runs the face tracking loop.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tello Face Tracking')
    parser.add_argument('--tello', action='store_true', help='Use Tello drone')
    parser.add_argument('--webcam', type=int, default=0, help='Webcam index')
    parser.add_argument('--resolution', nargs=2, type=int, default=[640, 480],
                       metavar=('WIDTH', 'HEIGHT'))
    parser.add_argument('--show', action='store_true', help='Show video feed')
    parser.add_argument('--save', action='store_true', help='Save video')
    args = parser.parse_args()

    # Initialize Tello drone if requested
    tello = None
    if args.tello:
        tello = Tello()
        tello.LOGGER.setLevel(logging.WARNING)  # Reduce log verbosity
        tello.connect()
        tello.streamon()
        time.sleep(2)  # Allow connection to establish

    # Set up video recording if enabled
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter('tracking.avi', fourcc, 20, 
                                      tuple(args.resolution))
    else:
        video_writer = None

    try:
        # Main control loop
        while True:
            # Get frame from drone or webcam
            if tello:
                frame = tello.get_frame_read().frame
                battery = tello.get_battery()
            else:
                # Use webcam as video source
                cap = cv2.VideoCapture(args.webcam)
                ret, frame = cap.read()
                if not ret:
                    break
                battery = 100  # Dummy value for webcam mode

            # Resize frame to requested resolution
            frame = cv2.resize(frame, tuple(args.resolution))
            
            # Process frame and get control velocities
            velocities = process_frame(
                frame,
                args.resolution,
                args.show,
                args.show
            )

            # Handle keyboard input for manual control
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        raise KeyboardInterrupt  # Clean exit
                    if tello:
                        if event.key == pygame.K_t:
                            tello.takeoff()      # Takeoff with 'T' key
                        elif event.key == pygame.K_l:
                            tello.land()         # Land with 'L' key

            # Send control commands to drone if it's flying
            if tello and tello.is_flying:
                tello.send_rc_control(*velocities)

            # Display video feed if requested
            if args.show:
                cv2.imshow("Tracking", frame)
                cv2.waitKey(1)  # Required for OpenCV window updates
                
            # Save video frame if recording is enabled
            if video_writer:
                video_writer.write(frame)

    except KeyboardInterrupt:
        print("Landing...")
    finally:
        # Clean up resources
        if tello:
            tello.land()
            tello.streamoff()
            tello.end()
        if video_writer:
            video_writer.release()
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    main()