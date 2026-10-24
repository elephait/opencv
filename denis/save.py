"""Rolling cache of recent video frames that can be saved as a clip.

Usage:
    from save import ClipCache
    clips = ClipCache(seconds=10)
    clips.add(frame)     # on every frame
    clips.save()         # writes clip_YYYYMMDD_HHMMSS.avi
"""
import os
import time
from collections import deque
from datetime import datetime

import cv2 as cv


class ClipCache:
    def __init__(self, seconds=10, save_dir=None):
        self.seconds = seconds
        self.save_dir = save_dir or os.path.dirname(os.path.abspath(__file__))
        self._frames = deque()  # (capture time, frame)

    def add(self, frame):
        """Cache a frame and drop anything older than `seconds`."""
        now = time.monotonic()
        self._frames.append((now, frame.copy()))
        while now - self._frames[0][0] > self.seconds:
            self._frames.popleft()

    def save(self):
        """Write the cached frames to a timestamped .avi. Returns the path or None."""
        frames = list(self._frames)  # snapshot
        if len(frames) < 2:
            print("Not enough frames cached yet.")
            return None

        duration = frames[-1][0] - frames[0][0]
        fps = (len(frames) - 1) / duration if duration > 0 else 20.0
        height, width = frames[0][1].shape[:2]
        path = os.path.join(self.save_dir, datetime.now().strftime("clip_%Y%m%d_%H%M%S.avi"))

        out = cv.VideoWriter(path, cv.VideoWriter_fourcc(*'XVID'), fps, (width, height))
        if not out.isOpened():
            print(f"Could not create video file: {path}")
            return None
        for _, frame in frames:
            out.write(frame)
        out.release()

        print(f"Saved {len(frames)} frames ({duration:.1f}s, {fps:.1f} fps): {path}")
        return path
