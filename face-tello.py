import cv2
from djitellopy import Tello
import argparse

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def showCam(img, imgsize):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (30,30)
            )

    for (x,y,w,h) in faces:
        cent_X = int(imgsize[0]/2)
        cent_Y = int(imgsize[1]/2)
        cent_box_X = int((w/2)+x)
        cent_box_Y = int((h/2)+y)

        size = 75
        area = (size*2) * (size*2)
        area_box = h * h

        cv2.circle(img, (cent_X, cent_Y), 2, (0, 0, 255), 2)
        cv2.rectangle(img, (int(cent_X-size), int(cent_Y-size)), (int(cent_X+size), int(cent_Y+size)), (0, 255, 0), 2)

        cv2.circle(img, (cent_box_X, cent_box_Y), 2, (0, 255, 0), 2)
        cv2.rectangle(img, (x,y), (x+h, y+h), (0, 255, 0), 2)

        eX = round((cent_X-cent_box_X) / cent_X * 100)
        eY = round((cent_Y-cent_box_Y) / cent_Y * 100)
        eZ = round((area-area_box) / area * 100)

        error_threshold = 10

        cv2.line(img, (int(imgsize[0]/2), int(imgsize[1]/2)), (int((w/2)+x), int((h/2)+y)), (0, 0, 255), 2)
        #print("x:{} | y:{} | w:{} | h:{} | eX:{} | eY:{} | eZ:{} ".format(x, y, w, h, eX, eY, eZ))

        lr_vel = 0
        fb_vel = 0
        up_val = 0
        y_val = 0

        if args.tello is False:
            if eX < -error_threshold or eX >= error_threshold:
                y_val = -eX
            else:
                y_val = 0

            if eY < -error_threshold or eY >= error_threshold:
                up_val = -eY
            else: 
                up_val = 0

            if eZ < -error_threshold or eZ >= error_threshold:
                fb_vel = eZ
            else: 
                fb_vel = 0

            print("x:{} | y:{} | w:{} | h:{} | eX:{} | eY:{} | eZ:{} | y_val:{} | up_val:{} | fb_vel:{}".format(x, y, w, h, eX, eY, eZ, y_val, up_val, fb_vel))
            tello.send_rc_control(lr_vel, fb_vel, up_val, y_val)

    cv2.imshow("Camera", img)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='DJI Tello Object Tracking\n')
    parser.add_argument('-tello', type=bool, help='Camera source, default is webcam', default=False)
    parser.add_argument('-vsize', nargs='+', type=int, default=[640, 480])

    args = parser.parse_args()

    if args.tello is True:
        print('Camera source is Tello')
        tello = Tello()
        tello.connect()
        print('Battery:',tello.get_battery())
        tello.streamoff()
        tello.streamon()
    else:
        print('Camera source is Webcam')
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, args.vsize[0])
        cap.set(4, args.vsize[1])

    while True:
        if args.tello is True:
            frame_read = tello.get_frame_read()
            myFrame = frame_read.frame
            img = cv2.resize(myFrame, args.vsize)
        else:
            ret, img = cap.read()
            if not ret:
                break
        
        showCam(img, args.vsize)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if args.tello is True:
                tello.streamoff()
            else:
                cap.release()
            cv2.destroyAllWindows()
            break