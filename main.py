import glob
import os
import time
from Send_alert import send_alert
import cv2
from datetime import datetime
from threading import Thread


video = cv2.VideoCapture(0)
first_frame = None
status_list = []
count = 1


def clean_folder():
    images = glob.glob("images/*.png")
    for img in images:
        os.remove(img)


while True:
    status = 0
    time.sleep(0.2)
    check, frame = video.read()
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grey_frame_gau = cv2.GaussianBlur(grey_frame, (5, 5), 0)

    if first_frame is None:
        first_frame = grey_frame_gau

    delta_frame = cv2.absdiff(first_frame, grey_frame_gau)
    thrash_frame = cv2.threshold(delta_frame, 65, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thrash_frame, None, iterations=2)
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 2000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/capture{count}.png", frame)
            count = count + 1
            obj_img = f"images/capture{int(count/2)}.png"

    status_list.append(status)
    status_list = status_list[-2:]
    if status_list[0] == 1 and status_list[1] == 0:

        thread1 = Thread(target=send_alert, args=(obj_img,))
        thread1.daemon = True
        thread1.start()

    now = datetime.now()
    cv2.putText(img=frame, text=now.strftime("%A"), org=(30, 40),
                fontFace=cv2.FONT_ITALIC, fontScale=1, color=(0, 255, 0))
    cv2.putText(img=frame, text=now.strftime("%H:%M:%S"), org=(30, 80),
                fontFace=cv2.FONT_ITALIC, fontScale=1, color=(255, 0, 0))
    cv2.imshow("video", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

thread2 = Thread(target=clean_folder())
thread2.daemon = True
thread2.start()
video.release()
