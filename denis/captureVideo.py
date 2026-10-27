import cv2 as cv
from save import ClipCache
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


# Keys that switch the stamp color
COLOR_KEYS = {'b': "blue", 'p': "pink", 'r': "red", 'o': "orange", 'm': "mono"}


def main():
    cap = open_camera()
    if cap is None:
        print("Cannot open camera")
        return

    stamp = Stamp("unicon.png")
    clips = ClipCache(seconds=10)
    print("Press 's' to save the last 10 seconds, 'q' to quit.")
    print("Stamp color: 'b' blue, 'p' pink, 'r' red, 'o' orange, 'm' black/white.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        stamp.apply(frame)   # logo on screen and in saved clips
        clips.add(frame)     # keep the last 10 seconds

        cv.imshow('Unicorn frame', frame)
        key = cv.waitKey(1) & 0xFF
        char = chr(key).lower()
        if char in COLOR_KEYS:
            if stamp.color != COLOR_KEYS[char]:
                stamp.set_color(COLOR_KEYS[char])
                print(f"Stamp color: {stamp.color}")
        elif key in (ord('s'), ord('S')):
            clips.save()
        elif key == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
    clips.wait()         # let any clip still being written finish


if __name__ == "__main__":
    main()
