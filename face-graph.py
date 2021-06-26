import cv2

cam_width = 640
cam_height = 480

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
video_capture = cv2.VideoCapture(0)

def camRun():
	while True:
		ret, frame = video_capture.read()
		if not ret:
			break

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (30,30)
		)

		for (x, y, w, h) in faces:
			cent_X = int(cam_width/2)
			cent_Y = int(cam_height/2)
			cent_box_X = int((w/2)+x)
			cent_box_Y = int((h/2)+y)

			cv2.circle(frame, (cent_X, cent_Y), 2, (0, 0, 255), 2)
			cv2.rectangle(frame, (x,y), (x+h, y+h), (0, 255, 0), 2)
			cv2.circle(frame, (cent_box_X, cent_box_Y), 2, (0, 255, 0), 2)
			print("x:{} | y:{} | w:{} | h:{} | eX:{} | eY:{} ".format(x, y, w, h, cent_box_X-cent_X, cent_box_Y-cent_Y))

		cv2.imshow('FaceDetection', frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	
	video_capture.release()
	cv2.destroyAllWindows()

camRun()