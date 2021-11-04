import numpy as np
import cv2
import cv2.aruco as aruco
import time
from threading import Thread
import commanding as c

cap = cv2.VideoCapture(1)
ISDETECTED = False
LIFTING = False
LOWERING = False
COUNTDOWN_FOR_LIFTING = 300
ALTITUDE = 10


def exportText(frame, text, state):
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "Dron durumu = " + state, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "Irtifa = " + str(ALTITUDE), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # print(text)


def waiting(frame):
    global DETECTED, LOWERING, LIFTING, COUNTDOWN_FOR_LIFTING
    print(COUNTDOWN_FOR_LIFTING / 60)
    if COUNTDOWN_FOR_LIFTING / 60 <= 0.0:
        exportText(frame, "", "YUKSELMEKTE")
        LIFTING = True
    else:
        exportText(frame, "Merkez tespit edilemedi, kalan sure: " + str(int(COUNTDOWN_FOR_LIFTING / 60)) + " saniye.",
                   "BEKLEMEDE")


def centroidDraw(frame, id, c):
    global LOWERING
    x1 = (c[0][0][0], c[0][0][1])
    x2 = (c[0][1][0], c[0][1][1])
    x3 = (c[0][2][0], c[0][2][1])
    x4 = (c[0][3][0], c[0][3][1])
    center = int((x1[0] + x3[0]) / 2), int((x1[1] + x3[1]) / 2)
    frame = cv2.circle(frame, center, 20, (0, 0, 255), 3)
    frame = cv2.line(frame, center, (int(frame.shape[1] / 2), int(frame.shape[0] / 2)), (0, 255, 255), 2)
    exportText(frame,
               "Center is " + str((int(frame.shape[1] / 2), int(frame.shape[0] / 2))) + " moving to " + str(center),
               "ALCALMAKTA")
    LOWERING = True
    return frame


vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter("qr.mp4", vid_cod, 60.0, (1920, 1080))


def preprocess():
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)
    arucoParameters = aruco.DetectorParameters_create()
    corners, ids, _ = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)
    # frame = aruco.drawDetectedMarkers(frame, corners)

    cv2.circle(frame, (int(frame.shape[1] / 2), int(frame.shape[0] / 2)), 6, (0, 255, 0), -1)

    return frame, ids, corners, gray


def main_loop():
    global DETECTED, LOWERING, LIFTING, COUNTDOWN_FOR_LIFTING

    while True:
        frame, ids, corners, gray = preprocess()

        if ids is not None:
            DETECTED = True
            LOWERING = True
            LIFTING = False
            COUNTDOWN_FOR_LIFTING = 300
            if 2 in ids:
                index = int(np.where(ids == 2)[0])
                frame = centroidDraw(frame, 2, corners[index])
            elif 1 in ids:
                index = int(np.where(ids == 1)[0])
                frame = centroidDraw(frame, 1, corners[index])
        else:
            DETECTED = False
            LOWERING = False
            waiting(frame)

        COUNTDOWN_FOR_LIFTING -= 1

        # output.write(frame)
        cv2.imshow('Display', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main_loop()
    output.release()
    cap.release()
    cv2.destroyAllWindows()
