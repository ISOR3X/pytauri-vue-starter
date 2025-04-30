import time

import cv2
import cv2.typing as cv2_t
import numpy as np

import pytauri_vue_starter.frame_controller.utils.shared_memory as shm


class FrameConsumer:
    def __init__(self, shm_names: list[str] | dict[str, int]):
        # Allow passing a dict as well, so both consumer and producer can use the same input args.
        if isinstance(shm_names, dict):
            items = list(shm_names.keys())
        else:
            items = shm_names

        for i in range(6):
            try:
                self.shm_list = {name: shm.create(name, True) for name in items}
                break
            except FileNotFoundError as e:
                print(e)
                print("Shm not found, retrying in 3s...", shm_names)
                time.sleep(3)
                continue

    def read_frame(self, shm_name: str = None, resolution: tuple[int, int] = (1920, 1080)) -> cv2_t.MatLike:
        if shm_name is None:
            shm_name = next(iter(self.shm_list))

        buf = self.shm_list[shm_name].buf
        return np.ndarray(
            (resolution[1], resolution[0], 3),
            dtype=np.uint8,
            buffer=buf,
        )

    def read_frames(self) -> dict[str, cv2_t.MatLike]:
        return {n: self.read_frame(n) for n in self.shm_list.keys()}

    @classmethod
    def frame_to_bytes(cls, frame: cv2_t.MatLike) -> bytes:
        _, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()

    @classmethod
    def bytes_to_frame(cls, b) -> cv2_t.MatLike:
        image_array = np.frombuffer(b, np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
