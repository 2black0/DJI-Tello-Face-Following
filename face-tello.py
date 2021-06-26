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
        cv2.circle(img, (int(imgsize[0]/2), int(imgsize[1]/2)), 2, (0, 0, 255), 2)
        cv2.rectangle(img, (x,y), (x+h, y+h), (0, 255, 0), 2)

        cv2.circle(img, (int((w/2)+x), int((h/2)+y)), 2, (0, 255, 0), 2)
        cv2.rectangle(img, (x,y), (x+h, y+h), (0, 255, 0), 2)

        cv2.line(img, (int(imgsize[0]/2), int(imgsize[1]/2)), (int((w/2)+x), int((h/2)+y)), (0, 0, 255), 2)
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

        while True:
            frame_read = tello.get_frame_read()
            myFrame = frame_read.frame
            img = cv2.resize(myFrame, args.vsize)

            showCam(img, args.vsize)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                tello.streamoff()
                cv2.destroyAllWindows()
                break

    else:
        print('Camera source is Webcam')
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, args.vsize[0])
        cap.set(4, args.vsize[1])

        while True:
            ret, img = cap.read()
            if not ret:
                break

            showCam(img, args.vsize)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                break