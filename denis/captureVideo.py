import numpy as np
import time
import cv2 as cv

def open_camera():
    # Windows: the default backend often fails on laptop cameras, so try
    # DirectShow and Media Foundation explicitly, across a few indexes.
    for backend_name, backend in (("DSHOW", cv.CAP_DSHOW), ("MSMF", cv.CAP_MSMF), ("ANY", cv.CAP_ANY)):
        for index in range(4):
            cap = cv.VideoCapture(index, backend)
            if cap.isOpened():
                print(f"Opened camera index {index} with {backend_name}")
                return cap
            cap.release()
    return None

SWITCH_SECONDS = 10  # toggle between color and gray every N seconds

cap = open_camera()
if cap is None:
    print("Cannot open camera")
    exit()
show_gray = False
last_switch = time.monotonic()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Switch between color and gray every SWITCH_SECONDS
    now = time.monotonic()
    if now - last_switch >= SWITCH_SECONDS:
        show_gray = not show_gray
        last_switch = now
    # Display the resulting frame
    if show_gray:
        cv.rectangle(frame,(384,0),(510,128),(0,255,0),3)
        cv.imshow('denis frame', cv.cvtColor(frame, cv.COLOR_BGR2GRAY))

    else:
        cv.imshow('original frame', frame)
    if cv.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()