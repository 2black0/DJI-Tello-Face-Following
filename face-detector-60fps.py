from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
detector = FaceDetector()
fpsReader = cvzone.FPS()

while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img)

    if bboxs:
        # bboxInfo - "id","bbox","score","center"
        center = bboxs[0]["center"]
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

    fps, img = fpsReader.update(img,pos=(10,30),color=(0,255,255),scale=2,thickness=2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
