import os

import cv2
import numpy as np

import pytauri_vue_starter.frame_controller.utils.shared_memory as shm


class FrameProducer:
    def __init__(self, ports: dict[str, int], resolution: tuple[int, int] = (1920, 1080)):
        """
        :param ports: Dictionary of camera ports. Key is the name of the camera and value is the port number.
        """
        self.cameras: dict[str, cv2.VideoCapture] = {}
        self.camera_ports: dict[str, int] = ports
        self.camera_memory: dict[str, shm.SharedMemory] = {}
        self.resolution = resolution

        for camera_name, camera_port in ports.items():
            self.camera_memory[camera_name] = shm.create(camera_name)
            self.cameras[camera_name] = self._init_camera(camera_port)

    def _init_camera(self, camera_port: int) -> cv2.VideoCapture:
        """
        Initialize camera with given camera port.
        """
        if os.name == "nt":
            cap = cv2.VideoCapture(camera_port, cv2.CAP_DSHOW)
        elif os.name == "posix":
            cap = cv2.VideoCapture(camera_port, cv2.CAP_V4L2)
        else:
            raise OSError("Unsupported operating system")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        cap.set(cv2.CAP_PROP_FPS, 30)

        return cap

    def __del__(self):
        for camera_name in self.camera_ports.keys():
            shm.close(camera_name)

    def start(self):
        frame_arrays = {
            n: np.ndarray(
                (self.resolution[1] // 2, self.resolution[0] // 2, 3),
                dtype=np.uint8,
                buffer=self.camera_memory[n].buf,
            )
            for n, p in self.camera_ports.items()
        }

        try:
            while True:
                for camera_name, camera_port in self.camera_ports.items():
                    ret, frame = self.cameras[camera_name].read()
                    frame = cv2.resize(frame, (self.resolution[0] // 2, self.resolution[1] // 2))

                    if not ret:
                        print("Failed to capture frame for camera: ", camera_name)
                        continue

                    np.copyto(frame_arrays[camera_name], frame)
                cv2.waitKey(30)
        finally:
            for n, c in self.cameras.items():
                c.release()
