from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory

import cv2
import numpy as np


class VideoConsumerProcess(Process):
    def __init__(self, resolution: tuple[int, int] = (1280, 720), shm_name="vpp_frame"):
        """
        Initialize the consumer process.

        :param resolution: A tuple of two integers representing the width and height of the video resolution.

        """
        super().__init__()

        self.resolution = resolution
        self.shm_name = shm_name
        self.shm: SharedMemory | None = None

    def run(self):
        """
        Main process function that reads frames
        """
        try:

            # Connect to frame shared memory
            self.shm = SharedMemory(self.shm_name, create=False)

            while True:
                # Create a numpy array using the shared memory buffer
                frame_array = np.ndarray((self.resolution[1], self.resolution[0], 3), dtype=np.uint8,
                                         buffer=self.shm.buf)

                self.process_frame(frame_array)

        finally:
            if self.shm:
                self.shm.close()
                self.shm.unlink()

    # noinspection PyMethodMayBeStatic
    def process_frame(self, frame: np.ndarray):
        """

        :param frame: A reference to the frame array.
        :return:
        """
        cv2.imshow("Video Consumer", frame)
        cv2.waitKey(1)
