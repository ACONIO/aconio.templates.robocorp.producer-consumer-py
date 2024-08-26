"""Module for screen recordings.

Adapted from:
https://github.com/robocorp/example-screen-recording

### Example Usage:
```python
from aconio import video 

video.recorder().start(filename="output/video.webm", max_length=10800)
video.recorder().stop()
```
"""

from __future__ import annotations

import os
import time
import queue
import threading

import cv2
import mss
import functools
import numpy as np
import pynput.mouse


@functools.lru_cache  # Always return the same instance.
def recorder() -> _Recorder:
    return _Recorder()


class _Recorder:
    """Record the screen and save the video to a file."""

    def __init__(self):
        self.capture_thread = None
        self.output_thread = None

        self.buffer = None
        self.filename = None
        self.monitor = None
        self.width = 0
        self.height = 0
        self.max_frame = 0
        self.fps = 0
        self.force_fps = False
        self.stop_capture = None

    def start(
        self,
        filename="output/video.webm",
        max_length=60,
        monitor=1,
        scale=1.0,
        fps=4,
        force_fps=False,
    ):
        """Start the recording."""

        self.filename = filename
        self.scale = float(scale)
        self.fps = int(fps)
        self.force_fps = force_fps

        with mss.mss() as sct:
            # Part of the screen to capture
            self.monitor = sct.monitors[int(monitor)]
            self.left = self.monitor["left"]
            self.top = self.monitor["top"]
            self.right = self.left + self.monitor["width"]
            self.bottom = self.top + self.monitor["height"]
            self.width = int(self.monitor["width"] * self.scale)
            self.height = int(self.monitor["height"] * self.scale)

        self.max_frame = self.fps * int(max_length)
        self.buffer = queue.Queue()

        self.stop_capture = threading.Event()

        self.output_thread = threading.Thread(
            name="Writer", target=self._write_file
        )
        self.capture_thread = threading.Thread(
            name="Capturer", target=self._capture
        )
        self.output_thread.start()
        self.capture_thread.start()

    def stop(self):
        """Stop the recording and save the video to a file."""
        if not self.stop_capture.is_set():
            self.stop_capture.set()
            self.capture_thread.join()
            self.output_thread.join()

    def cancel(self):
        """Stop the recording and delete the file."""
        self.stop()
        os.remove(self.filename)

    def _write_file(self):
        cur_frame = 0
        prev_frame = None
        out_frame = None

        fourcc = cv2.VideoWriter_fourcc(*"VP80")

        with _SuppressStderr():
            out = cv2.VideoWriter(
                self.filename, fourcc, self.fps, (self.width, self.height)
            )

        while cur_frame < self.max_frame:
            data = self.buffer.get()
            if data is None:
                break

            ts, img, mouse = data
            frame = np.array(img)

            if self.force_fps:
                while ts > (cur_frame + 1) / self.fps:
                    cur_frame += 1
                    out.write(out_frame)
            else:
                if prev_frame is not None and (prev_frame == frame).all():
                    continue

            cur_frame += 1
            prev_frame = frame

            frame = cv2.resize(frame, (self.width, self.height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            x, y = mouse
            if self.left <= x < self.right and self.top <= y < self.bottom:
                x = int((x - self.left) * self.scale)
                y = int((y - self.top) * self.scale)
                r = int(self.width * self.scale / 100)
                w = max(1, round(self.width * self.scale / 500))
                cv2.circle(frame, (x, y), r, (0, 0, 255), w)

            out_frame = cv2.putText(
                frame,
                "{0:.2f}".format(ts),  # pylint: disable=consider-using-f-string
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                4,
            )
            out.write(out_frame)

        self.stop_capture.set()
        out.release()

    def _capture(self):
        mouse = pynput.mouse.Controller()
        with mss.mss() as sct:
            frame_number = 0
            start_time = time.time()

            while not self.stop_capture.is_set():
                trigger_time = start_time + frame_number / self.fps
                while time.time() < trigger_time:
                    time.sleep(0.001)

                # Get raw pixels from the screen, save it to a Numpy array
                # frame = np.array(sct.grab(self.monitor))
                self.buffer.put_nowait(
                    (
                        time.time() - start_time,
                        sct.grab(self.monitor),
                        mouse.position,
                    )
                )

                frame_number += 1

        self.buffer.put_nowait(None)


class _SuppressStderr(object):
    """Reassign stderr to /dev/null.

    ### Usage:
    ```python
    print("This will be printed.", file=sys.stderr)

    with SuppressStderr():
        print("This will not be printed.", file=sys.stderr)

    """

    def __init__(self):
        # Open a null file
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        # Save the actual stderr (2) file descriptor.
        self.save_fd = os.dup(2)

    def __enter__(self):
        # Assign the null pointer to stderr.
        os.dup2(self.null_fd, 2)

    def __exit__(self, *_):
        # Re-assign the real stderr back to (2)
        os.dup2(self.save_fd, 2)
        # Close all file descriptors
        os.close(self.null_fd)
        os.close(self.save_fd)
