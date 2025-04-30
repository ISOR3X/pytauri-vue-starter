import logging

import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame


class CustomVideoStreamTrack(VideoStreamTrack):
    def __init__(self, port: int):
        super().__init__()

        self.logger = logging.getLogger("candela")
        self.logger.info(f"Initializing camera with shm name: {port}")

        self.cap = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.cap.read()
        self.frame_count = 0

    async def recv(self):
        self.frame_count += 1
        print("test")

        _, frame = self.cap.read()

        pts, time_base = await self.next_timestamp()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame
