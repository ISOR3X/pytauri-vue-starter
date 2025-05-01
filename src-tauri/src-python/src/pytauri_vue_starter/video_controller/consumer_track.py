from multiprocessing.shared_memory import SharedMemory

import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame


class ConsumerTrack(VideoStreamTrack):
    def __init__(self, resolution: tuple[int, int] = (1280, 720), shm_name="vpp_frame"):
        super().__init__()

        self.resolution = resolution

        self.frame_count = 0
        self.shm = SharedMemory(shm_name, create=False)

    async def recv(self):
        self.frame_count += 1

        pts, time_base = await self.next_timestamp()

        frame_array = np.ndarray((self.resolution[1], self.resolution[0], 3), dtype=np.uint8,
                                 buffer=self.shm.buf)

        video_frame = VideoFrame.from_ndarray(frame_array, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame
