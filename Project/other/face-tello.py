import cv2
from djitellopy import Tello
import argparse
import keyboard 
import logging

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def showCam(img, imgsize, tellos, status):
    vel = [0, 0, 0, 0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5, minSize = (30,30))

    for (x,y,w,h) in faces:
        vel = [0, 0, 0, 0]
        cent_X = int(imgsize[0]/2)
        cent_Y = int(imgsize[1]/2)
        cent_box_X = int((w/2)+x)
        cent_box_Y = int((h/2)+y)

        size = 25
        area = (size*2) * (size*2)
        area_box = h * h
        error_threshold = 2

        eX = round((cent_X-cent_box_X) / cent_X * 100)
        eY = round((cent_Y-cent_box_Y) / cent_Y * 100)
        eZ = round((area-area_box) / area * 12.5)

        cv2.circle(img, (cent_X, cent_Y), 2, (0, 0, 255), 2)
        cv2.rectangle(img, (int(cent_X-size), int(cent_Y-size)), (int(cent_X+size), int(cent_Y+size)), (0, 255, 0), 2)
        cv2.circle(img, (cent_box_X, cent_box_Y), 2, (0, 255, 0), 2)
        cv2.rectangle(img, (x,y), (x+h, y+h), (0, 255, 0), 2)
        cv2.line(img, (int(imgsize[0]/2), int(imgsize[1]/2)), (int((w/2)+x), int((h/2)+y)), (0, 0, 255), 2)

        if tellos is True and status is True:
            if eX < -error_threshold or eX >= error_threshold:
                vel[3] = -eX
            if eY < -error_threshold or eY >= error_threshold:
                vel[2] = eY
            if eZ < -error_threshold or eZ >= error_threshold:
                vel[1] = eZ
        print("x:{} | y:{} | w:{} | h:{} | eX:{} | eY:{} | eZ:{} | y_val:{} | up_val:{} | fb_vel:{}".format(x, y, w, h, eX, eY, eZ, vel[3], vel[2], vel[1]))

    cv2.imshow("Camera", img)
    return (vel)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='DJI Tello Object Tracking\n')
    parser.add_argument('-tello', type=bool, help='Camera source, default is webcam', default=False)
    parser.add_argument('-vsize', nargs='+', type=int, default=[640, 480])

    args = parser.parse_args()

    if args.tello is True:
        print('Camera source is Tello')
        tello = Tello()
        tello.LOGGER.setLevel(logging.WARNING)
        tello.connect()
        print('Battery:',tello.get_battery())
        tello.streamoff()
        tello.streamon()
    else:
        print('Camera source is Webcam')
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, args.vsize[0])
        cap.set(4, args.vsize[1])

    status_flying = False
    while True:
        if args.tello is True:
            frame_read = tello.get_frame_read()
            myFrame = frame_read.frame
            img = cv2.resize(myFrame, args.vsize)

            if keyboard.is_pressed('t') and status_flying is False:
                status_flying = True
                tello.takeoff()
        else:
            status_flying = True
            ret, img = cap.read()
            if not ret:
                break
        
        lr_vel, fb_vel, up_vel, y_vel = showCam(img, args.vsize, args.tello, status_flying)
        
        if args.tello is True and status_flying is True:
            height = tello.get_height()
            if height > 30:
                tello.send_rc_control(lr_vel, fb_vel, up_vel, y_vel)

        if cv2.waitKey(1) & 0xFF == ord('l'):
            if args.tello is True:
                tello.land()
                tello.streamoff()
            else:
                cap.release()
            cv2.destroyAllWindows()
            break