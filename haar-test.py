import cv2
import os
import numpy as np
import glob

image_path = "./face-image/"
#image_list = os.listdir(image_path)

trained_face_data = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def check_image(path):
    for image in glob.glob(path + "*.jpg"):
        #print("load image:", image)
        img = cv2.imread(image)
        height = 224
        width = img.shape[1]*height/img.shape[0]
        img = cv2.resize(img, (int(width), height), None, 0.5, 0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow('img', img)
        cv2.waitKey(0)    
        
def haar_face(path):
    for image in glob.glob(path + "*.jpg"):
        #print("load image:", image)
        img = cv2.imread(image)
        height = 500
        width = img.shape[1]*height/img.shape[0]
        img = cv2.resize(img, (int(width), height), None, 0.5, 0.5, interpolation=cv2.INTER_AREA)
        detect_faces(img)

def detect_faces(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_coordinates = trained_face_data.detectMultiScale(gray_img)
    for coordinate in face_coordinates:
        (x, y, w, h) = coordinate
        colors = np.random.randint(1, 255, 3)
        cv2.rectangle(image, (x, y), (x + w, y + h), (int(colors[0]), int(colors[1]), int(colors[2])), thickness=2)
    cv2.imshow('Image', image)
    cv2.waitKey(0)

haar_face(image_path)