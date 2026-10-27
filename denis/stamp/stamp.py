"""Logo stamp for video frames.

Usage:
    from stamp import Stamp
    stamp = Stamp("unicon.png")              # path may be relative to this file
    stamp = Stamp("unicon.png", color="pink")  # any name in COLORS; default "mono"
    stamp.set_color("blue")                    # change it later
    ...
    stamp.apply(frame)               # call on every frame (modifies it in place)
"""
import os

import cv2 as cv
import numpy as np

STAMP_WIDTH_RATIO = 0.12   # stamp width as a fraction of the frame width
STAMP_MARGIN_RATIO = 0.02    # left gap, as a fraction of frame width
STAMP_MARGIN_Y_RATIO = 0.06  # top gap, as a fraction of frame width

# The logo is drawn in one color: the dark shade on bright footage, the light
# shade when the area under it is dark. Two thresholds (hysteresis) stop flickering.
# name: (dark, light), both BGR
COLORS = {
    "mono":   ((0, 0, 0),      (255, 255, 255)),  # black / white
    "pink":   ((70, 30, 170),  (200, 170, 255)),
    "red":    ((20, 20, 160),  (150, 150, 255)),
    "blue":   ((140, 40, 10),  (255, 200, 150)),
    "green":  ((30, 110, 20),  (170, 240, 160)),
    "purple": ((120, 30, 90),  (240, 180, 220)),
    "orange": ((0, 90, 200),   (140, 200, 255)),
}
DEFAULT_COLOR = "mono"
DARK_BELOW = 90                # go light when background brightness < this
LIGHT_ABOVE = 130              # go back to dark when brightness > this


class Stamp:
    def __init__(self, path, color=DEFAULT_COLOR):
        self.set_color(color)
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        self.path = path
        self._image = self._load(path)  # (bgr, alpha) at original size, or None
        self._scaled = None             # (bgr, alpha) resized for the frame
        self._frame_width = None
        self._use_light = False
        self._smoothed = None

    def set_color(self, color):
        """Switch to a named color pair from COLORS (can be called any time)."""
        if color not in COLORS:
            raise ValueError(f"Unknown stamp color {color!r}; choose from {', '.join(COLORS)}")
        dark, light = COLORS[color]
        self.color = color
        self._dark = np.array(dark, np.float32)
        self._light = np.array(light, np.float32)

    @staticmethod
    def _load(path):
        """Load the image as BGR + alpha (0..1). Returns (bgr, alpha) or None."""
        img = cv.imread(path, cv.IMREAD_UNCHANGED)
        if img is None:
            print(f"Cannot load stamp image: {path}")
            return None
        if img.ndim == 2:
            img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        if img.shape[2] == 4:
            bgr = img[:, :, :3]
            alpha = img[:, :, 3].astype(np.float32) / 255.0
        else:
            bgr = img
            alpha = np.ones(img.shape[:2], np.float32)
        return bgr, alpha

    def _scale(self, frame_width):
        """Resize the stamp to a fraction of the frame width."""
        bgr, alpha = self._image
        w = max(1, int(frame_width * STAMP_WIDTH_RATIO))
        h = max(1, int(bgr.shape[0] * w / bgr.shape[1]))
        bgr = cv.resize(bgr, (w, h), interpolation=cv.INTER_AREA)
        alpha = cv.resize(alpha, (w, h), interpolation=cv.INTER_AREA)
        self._scaled = (bgr, alpha[:, :, None])
        self._frame_width = frame_width

    def apply(self, frame):
        """Blend the stamp onto the top-left corner of the frame (in place)."""
        if self._image is None:
            return frame
        fh, fw = frame.shape[:2]
        if self._scaled is None or self._frame_width != fw:
            self._scale(fw)
        bgr, alpha = self._scaled
        h, w = bgr.shape[:2]
        margin = int(fw * STAMP_MARGIN_RATIO)
        y = int(fw * STAMP_MARGIN_Y_RATIO)
        x = margin  # top-left corner
        if y < 0 or x < 0:
            return frame

        roi = frame[y:y + h, x:x + w]

        # Brightness under the stamp, smoothed over frames, with hysteresis
        b = float(cv.cvtColor(roi, cv.COLOR_BGR2GRAY).mean())
        self._smoothed = b if self._smoothed is None else 0.9 * self._smoothed + 0.1 * b
        if self._use_light and self._smoothed > LIGHT_ABOVE:
            self._use_light = False
        elif not self._use_light and self._smoothed < DARK_BELOW:
            self._use_light = True

        fg = self._light if self._use_light else self._dark
        frame[y:y + h, x:x + w] = (alpha * fg + (1.0 - alpha) * roi).astype(np.uint8)
        return frame
