import cv2
from djitellopy import Tello
import argparse
import keyboard 
import logging

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def showCam(img, imgsize, tellos, status, data, debug, box, osd, save, video):
    vel = [0, 0, 0, 0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5, minSize = (30,30))

    for (x,y,w,h) in faces:
        vel = [0, 0, 0, 0]
        cent_X = int(imgsize[0]/2)
        cent_Y = int(imgsize[1]/2)
        cent_box_X = int((w/2)+x)
        cent_box_Y = int((h/2)+y)

        size = 40
        area = (size*2) * (size*2)
        area_box = h * h
        error_threshold = 2

        eX = round((cent_X-cent_box_X) / cent_X * 100)
        eY = round((cent_Y-cent_box_Y) / cent_Y * 100)
        eZ = round((area-area_box) / area * 15)

        if box is True:
            cv2.circle(img, (cent_X, cent_Y), 2, (0, 0, 255), 2)
            cv2.rectangle(img, (int(cent_X-size), int(cent_Y-size)), (int(cent_X+size), int(cent_Y+size)), (0, 255, 0), 2)
            cv2.circle(img, (cent_box_X, cent_box_Y), 2, (0, 255, 0), 2)
            cv2.rectangle(img, (x,y), (x+h, y+h), (0, 255, 0), 2)
            cv2.line(img, (int(imgsize[0]/2), int(imgsize[1]/2)), (int((w/2)+x), int((h/2)+y)), (0, 0, 255), 2)

        if osd is True:
            cv2.putText(img, 'B:'+str(data[0])+' H:'+str(data[1])+' FT:'+str(data[2])+' T:'+str(data[9]), (10, imgsize[1]-10), 2, 1, (0, 255, 0), 2)
            cv2.putText(img, 'R:'+str(data[3])+' P:'+str(data[4])+' Y:'+str(data[5]), (10, 30), 2, 1, (0, 255, 0), 2)
            cv2.putText(img, 'X:'+str(data[6])+' Y:'+str(data[7])+' Z:'+str(data[8]), (imgsize[0]-290, 30), 2, 1, (0, 255, 0), 2)

        if tellos is True and status is True:
            if eX < -error_threshold or eX >= error_threshold:
                vel[3] = -eX
            if eY < -error_threshold or eY >= error_threshold:
                vel[2] = eY
            if eZ < -error_threshold or eZ >= error_threshold:
                vel[1] = eZ

        if debug is True:
            print("x:{} | y:{} | w:{} | h:{} | eX:{} | eY:{} | eZ:{} | y_val:{} | up_val:{} | fb_vel:{}".format(x, y, w, h, eX, eY, eZ, vel[3], vel[2], vel[1]))

    cv2.imshow("Camera", img)
    if save is True:
        video.write(img)
    return (vel)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='DJI Tello Object Tracking\n')
    parser.add_argument('-tello', type=bool, help='Camera source, default is webcam', default=False)
    parser.add_argument('-vsize', nargs='+', type=int, default=[640, 480])
    parser.add_argument('-debug', type=bool, help='Enable debug', default=False)
    parser.add_argument('-box', type=bool, help='Enable bounding box', default=True)
    parser.add_argument('-osd', type=bool, help='Enable on screen display', default=False)
    parser.add_argument('-save', type=bool, help='Save video', default=False)

    args = parser.parse_args()

    if args.tello is True:
        print('Camera source is Tello')
        tello = Tello()
        tello.LOGGER.setLevel(logging.WARNING)
        tello.connect()
        tello.streamoff()
        tello.streamon()
    else:
        print('Camera source is Webcam')
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, args.vsize[0])
        cap.set(4, args.vsize[1])

    videoWriter = 0
    if args.save is True:
        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        videoWriter = cv2.VideoWriter('./video.avi', fourcc, 20, (args.vsize[0],args.vsize[1]))
    
    status_flying = False
    status_detect = False
    while True:
        if args.tello is True:
            frame_read = tello.get_frame_read()
            myFrame = frame_read.frame
            img = cv2.resize(myFrame, args.vsize)

            battery = tello.get_battery()
            height = tello.get_height()
            flight_time = tello.get_flight_time()
            roll = tello.get_roll()
            pitch = tello.get_pitch()
            yaw = tello.get_yaw()
            speed_x = tello.get_speed_x()
            speed_y = tello.get_speed_y()
            speed_z = tello.get_speed_z()
            temp = tello.get_temperature()
            
            if keyboard.is_pressed('t') and status_flying is False:
                status_flying = True
                tello.takeoff()
        else:
            battery = 0
            height = 0
            flight_time = 0
            roll = 0
            pitch = 0
            yaw = 0
            speed_x = 0
            speed_y = 0
            speed_z = 0
            temp = 0

            status_flying = True
            ret, img = cap.read()
            if not ret:
                break
        
        data = [battery, height, flight_time, roll, pitch, yaw, speed_x, speed_y, speed_z, temp]
        lr_vel, fb_vel, up_vel, y_vel = showCam(img, args.vsize, args.tello, status_flying, data, args.debug, args.box, args.osd, args.save, videoWriter)
        
        if keyboard.is_pressed('d') and status_detect is False:
            status_detect = True        
        if keyboard.is_pressed('s') and status_detect is True:
            status_detect = False

        if args.tello is True and status_flying is True and status_detect is True:
            height = tello.get_height()
            if height > 30:
                tello.send_rc_control(lr_vel, fb_vel, up_vel, y_vel)
        else:
            tello.send_rc_control(0, 0, 0, 0)
    

        if (cv2.waitKey(1) & 0xFF == ord('l')):
            if args.tello is True:
                height = tello.get_height()
                if height > 30:
                    tello.land()
                tello.streamoff()
            else:
                cap.release()
            if args.save is True:
                videoWriter.release()
            cv2.destroyAllWindows()
            break