"""Rolling cache of recent video frames that can be saved as a clip.

Usage:
    from save import ClipCache
    clips = ClipCache(seconds=10)
    clips.add(frame)     # on every frame
    clips.save()         # writes clip_YYYYMMDD_HHMMSS.avi in the background
    clips.wait()         # before exiting, finish any saves still writing
"""
import os
import threading
import time
from collections import deque
from datetime import datetime

import cv2 as cv


class ClipCache:
    def __init__(self, seconds=10, save_dir=None):
        self.seconds = seconds
        self.save_dir = save_dir or os.path.dirname(os.path.abspath(__file__))
        self._frames = deque()  # (capture time, frame)
        self._writers = []      # background save threads

    def add(self, frame):
        """Cache a frame and drop anything older than `seconds`."""
        now = time.monotonic()
        self._frames.append((now, frame.copy()))
        while now - self._frames[0][0] > self.seconds:
            self._frames.popleft()

    def save(self):
        """Start writing the cached frames to a timestamped .avi in the background.

        Returns the path the clip will be written to, or None if too few frames.
        """
        frames = list(self._frames)  # snapshot; add() keeps going while we write
        if len(frames) < 2:
            print("Not enough frames cached yet.")
            return None

        path = os.path.join(self.save_dir, datetime.now().strftime("clip_%Y%m%d_%H%M%S.avi"))
        self._writers = [t for t in self._writers if t.is_alive()]
        writer = threading.Thread(target=_write_clip, args=(frames, path), name="clip-writer")
        writer.start()
        self._writers.append(writer)
        print(f"Saving {len(frames)} frames to {path} ...")
        return path

    def wait(self):
        """Block until every background save has finished."""
        for writer in self._writers:
            writer.join()
        self._writers.clear()


def _write_clip(frames, path):
    """Encode (capture time, frame) pairs to `path`. Runs on a worker thread."""
    duration = frames[-1][0] - frames[0][0]
    fps = (len(frames) - 1) / duration if duration > 0 else 20.0
    height, width = frames[0][1].shape[:2]

    out = cv.VideoWriter(path, cv.VideoWriter_fourcc(*'XVID'), fps, (width, height))
    if not out.isOpened():
        print(f"Could not create video file: {path}")
        return
    for _, frame in frames:
        out.write(frame)
    out.release()

    print(f"Saved {len(frames)} frames ({duration:.1f}s, {fps:.1f} fps): {path}")
