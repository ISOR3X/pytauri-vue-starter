import asyncio
import multiprocessing
from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory

import cv2
import numpy as np
from aiortc.contrib.media import MediaPlayer
from av import VideoFrame


class VideoProducerProcess(Process):
    def __init__(self, camera_name="video=HP HD Camera", framerate: int = 30, resolution: tuple[int, int] = (1280, 720),
                 shm_name="vpp_frame"):
        """
        Initializes the producer process.

        :param camera_name: A string representing the name or identifier of the camera device.
        :param framerate: Integer is representing the video framerate in frames per second.
        :param resolution: A tuple of two integers representing the width and height
            of the video resolution.

        """
        super().__init__()
        self.camera_name = camera_name
        self.shm_name = shm_name
        self.options = {"framerate": str(framerate), "video_size": "x".join(map(str, resolution))}

        self.exit = multiprocessing.Event()
        self.shm: SharedMemory | None = None

    @property
    def has_initialized(self) -> bool:
        return self.shm is not None

    async def _async_run(self):
        mp = MediaPlayer(
            self.camera_name, format="dshow", options=self.options
        )
        video_track = mp.video

        # Convert frame to ndarray to calculate the size for the shared memory.
        frame = await video_track.recv()
        assert isinstance(frame, VideoFrame)
        frame_array = frame.to_ndarray(format="rgb24")
        self.shm = SharedMemory(self.shm_name, create=True, size=frame_array.nbytes)

        while not self.exit.is_set():
            frame = await video_track.recv()
            assert isinstance(frame, VideoFrame)

            # Convert frame to ndarray
            frame_array = frame.to_ndarray(format="rgb24")
            frame_array = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)

            # Copy frame data to shared memory
            np_array = np.ndarray(frame_array.shape, dtype=frame_array.dtype, buffer=self.shm.buf)
            np_array[:] = frame_array[:]

    def run(self):
        try:
            asyncio.run(self._async_run())
        finally:
            self.terminate()

    def terminate(self):
        self.exit.set()
        self.shm.close()
        self.shm.unlink()
        super().terminate()
