import cv2
from djitellopy import Tello
import argparse
import keyboard 
import logging

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#parameter control
error_threshold = 2
size = 40

def calculateError(centerX, centerY, centerH, centerBoxX, centerBoxY, boxH):
    error = [round((centerX - centerBoxX) / centerX * 100), #error X
             round((centerY - centerBoxY) / centerY * 100), #error Y
             round((centerH - boxH/2) / centerH * 100) #error Z
            ]
    a = 0
    for i in error:
        if i >= 100:
            error[a] = 100
        if i <= -100:
            error[a] = 100
        a += 1
    return error

def showCam(img, imgsize, tellos, status, data, debug, box, osd, save, video):
    global error_threshold
    global size
    vel = [0, 0, 0, 0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5, minSize = (30,30))

    for (x, y, w, h) in faces:
        cent_X = int(imgsize[0]/2)
        cent_Y = int(imgsize[1]/2)
        cent_box_X = int((w/2)+x)
        cent_box_Y = int((h/2)+y)

        error = calculateError(cent_X, cent_Y, size, cent_box_X, cent_box_Y, h)

        if box is True:
            cv2.circle(img, (cent_X, cent_Y), 2, (0, 0, 255), 2)
            cv2.rectangle(img, (int(cent_X-size), int(cent_Y-size)), (int(cent_X+size), int(cent_Y+size)), (0, 255, 0), 2)
            cv2.circle(img, (cent_box_X, cent_box_Y), 2, (0, 255, 0), 2)
            cv2.rectangle(img, (x,y), (x+h, y+h), (0, 255, 0), 2)
            cv2.line(img, (int(imgsize[0]/2), int(imgsize[1]/2)), (int((w/2)+x), int((h/2)+y)), (0, 0, 255), 2)

        if osd is True:
            cv2.putText(img, 'B:'+str(data[0])+' H:'+str(data[1])+' FT:'+str(data[2])+' T:'+str(data[9]), (10, imgsize[1]-10), 2, 1, (0, 255, 0), 2)
            cv2.putText(img, 'R:'+str(data[3])+' P:'+str(data[4])+' Y:'+str(data[5]), (10, 30), 2, 1, (0, 255, 0), 2)
            cv2.putText(img, 'eX:'+str(error[0])+' eY:'+str(error[1])+' eZ:'+str(error[2]), (imgsize[0]-350, 30), 2, 1, (0, 255, 0), 2)
            #cv2.putText(img, 'X:'+str(data[6])+' Y:'+str(data[7])+' Z:'+str(data[8]), (imgsize[0]-290, 30), 2, 1, (0, 255, 0), 2)

        if tellos is True and status is True:
            if error[0] < -error_threshold or error[0] >= error_threshold:
                vel[3] = -error[0]
            if error[1] < -error_threshold or error[1] >= error_threshold:
                vel[2] = error[1]
            if error[2] < -error_threshold or error[2] >= error_threshold:
                vel[1] = error[2]

        if debug is True:
            print("x:{} | y:{} | w:{} | h:{} | eX:{} | eY:{} | eZ:{} | y_val:{} | up_val:{} | fb_vel:{}".format(x, y, w, h, error[0], error[1], error[2], vel[3], vel[2], vel[1]))

    cv2.imshow("Camera", img)
    if save is True:
        video.write(img)
    return (vel)

def getStatus(tello):
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

    return (battery, height, flight_time, roll, pitch, yaw, speed_x, speed_y, speed_z, temp)

def main():
    #parsing for argument
    parser = argparse.ArgumentParser(description='DJI Tello Object Tracking\n')
    parser.add_argument('-tello', type=bool, help='Camera source, default is webcam', default=False)
    parser.add_argument('-vsize', nargs='+', type=int, default=[640, 480])
    parser.add_argument('-debug', type=bool, help='Enable debug', default=False)
    parser.add_argument('-box', type=bool, help='Enable bounding box', default=True)
    parser.add_argument('-osd', type=bool, help='Enable on screen display', default=False)
    parser.add_argument('-save', type=bool, help='Save video', default=False)

    args = parser.parse_args()

    #check source, tello or webcam
    if args.tello is True:
        print('Camera source is Tello')
        tello = Tello()
        tello.LOGGER.setLevel(logging.WARNING) #disable warning message from djitellopy module in terminal
        tello.connect()
        tello.streamoff()
        tello.streamon()
        frame_read = tello.get_frame_read()
    else:
        print('Camera source is Webcam')
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, args.vsize[0])
        cap.set(4, args.vsize[1])

    #option for save the video
    videoWriter = 0
    if args.save is True:
        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        videoWriter = cv2.VideoWriter('./video.avi', fourcc, 20, (args.vsize[0],args.vsize[1]))
    
    #looping for get data from camera and feed into face recognition to calculate the error
    status_flying = False
    status_detect = False
    while True:
        #getting image from tello
        if args.tello is True:
            img = frame_read.frame
            img = cv2.resize(img, args.vsize)

            #get status of tello
            stat = getStatus(tello)
           
            if keyboard.is_pressed('t') and status_flying is False:
                status_flying = True
                tello.takeoff()
        #getting image from webcam
        else:
            #for camera status is 0 and status flying is True
            stat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            status_flying = True
            ret, img = cap.read()
            if not ret:
                break
        
        velocity = showCam(img, args.vsize, args.tello, status_flying, stat, args.debug, args.box, args.osd, args.save, videoWriter)
        
        #enable / disable detection mode
        if keyboard.is_pressed('d') and status_detect is False:
            status_detect = True        
        if keyboard.is_pressed('s') and status_detect is True:
            status_detect = False

        #signal control the drone
        if args.tello is True and status_flying is True and status_detect is True:
            height = tello.get_height()
            if height > 30:
                tello.send_rc_control(velocity[0], velocity[1], velocity[2], velocity[3])
        elif args.tello is True and status_detect is False:
            tello.send_rc_control(0, 0, 0, 0)
    

        #close the camera, land the drone and exit from looping
        if (cv2.waitKey(1) & 0xFF == ord('l')):
            if args.tello is True:
                height = tello.get_height()
                if height > 30:
                    tello.land()
                frame_read.stop()    
                tello.streamoff()
            else:
                cap.release()
            if args.save is True:
                videoWriter.release()
            cv2.destroyAllWindows()
            break

if __name__=="__main__":
    main()