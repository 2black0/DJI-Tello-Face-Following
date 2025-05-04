# OpenCV program to detect face in real time
# import libraries of python OpenCV 
# where its functionality resides
import cv2 
import requests
import argparse 
import os
  
# parse arguments
parser = argparse.ArgumentParser(description='YOLO Face Detection')
parser.add_argument('--src', action='store', default=0, nargs='?', help='Set video source; default is usb webcam')
parser.add_argument('--w', action='store', default=320, nargs='?', help='Set video width')
parser.add_argument('--h', action='store', default=240, nargs='?', help='Set video height')
args = parser.parse_args()
 
# face detection endpoint (deepsight sdk runs as http service on port 5000)
face_api = &amp;amp;amp;amp;quot;http://127.0.0.1:5000/inferImage?detector=yolo&amp;amp;amp;amp;quot;
 
# capture frames from a camera
cap = cv2.VideoCapture(args.src)
 
# loop runs if capturing has been initialized.
while 1:    
         
    # reads frames from a camera
    ret, img = cap.read() 
    img = cv2.resize(img, (int(args.w),int(args.h)))    
    r, imgbuf = cv2.imencode(&amp;amp;amp;amp;quot;.bmp&amp;amp;amp;amp;quot;, img)    
    image = {'pic':bytearray(imgbuf)}
      
    r = requests.post(face_api, files=image)
    result = r.json()   
      
    if len(result) &amp;amp;amp;amp;gt; 1:
        faces = result[:-1]
        for face in faces:
            rect = [face[i] for i in ['faceRectangle']][0]
            x,y,w,h, confidence = [rect[i] for i in ['left', 'top', 'width', 'height', 'confidence']]
            # discard if confidence is too low
            if confidence &amp;amp;amp;amp;lt; 0.6:
                continue
                 
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,255),4,8) 
 
     
    cv2.imshow('YOLO Face detection',img)
  
    # Wait for Esc key to stop
    if cv2.waitKey(1) &amp;amp;amp;amp;amp; 0xff == 27:
        break
  
# Close the window
cap.release()
  
# De-allocate any associated memory usage
cv2.destroyAllWindows()