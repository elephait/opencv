import cv2 as cv
from stamp.stamp import Stamp

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

cap = open_camera()
if cap is None:
    print("Cannot open camera")
    exit()

stamp = Stamp("unicon.png")
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Stamp the logo onto the frame
    stamp.apply(frame)

    # Display the resulting frame
    cv.imshow('Uniocon Video', frame)
    if cv.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
