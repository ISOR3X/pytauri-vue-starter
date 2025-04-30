import threading
from multiprocessing import resource_tracker as _mp_rt
from multiprocessing import shared_memory as _mp_shm


# Fix for resource tracking of shared memory on linux. See https://github.com/python/cpython/issues/82300
class SharedMemory(_mp_shm.SharedMemory):
    __lock = threading.Lock()

    def __init__(
            self,
            name: str | None = None,
            create: bool = False,
            size: int = 0,
            *,
            track: bool = False,
    ) -> None:
        self._track = track

        # if tracking, normal init will suffice
        if track:
            super().__init__(name=name, create=create, size=int(size))
            return

        # lock so that other threads don't attempt to use the
        # register function during this time
        with self.__lock:
            # temporarily disable registration during initialization
            orig_register = _mp_rt.register
            _mp_rt.register = self.__tmp_register

            # initialize; ensure original register function is re-instated
            try:
                super().__init__(name=name, create=create, size=size)
            finally:
                _mp_rt.register = orig_register

    @staticmethod
    def __tmp_register(*args, **kwargs) -> None:
        return

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def unlink(self) -> None:
        if _mp_shm._USE_POSIX and self._name:
            _mp_shm._posixshmem.shm_unlink(self._name)
            if self._track:
                _mp_rt.unregister(self._name, "shared_memory")


def close(shm_name):
    try:
        shm = SharedMemory(name=shm_name)
        shm.close()
        shm.unlink()
        print(f"shm '{shm_name}' closed and unlinked.")
    except FileNotFoundError:
        print(f"shm '{shm_name}' does not exist.")
    except Exception as e:
        print(f"error while trying to close and unlink shm '{shm_name}': {e}")


def create(shm_name, force_read: bool = False, resolution: tuple[int, int] = (1920, 1080)):
    frame_size = resolution[0] * resolution[1] * 3
    try:
        if force_read:
            shm = SharedMemory(name=shm_name)
            return shm
        shm = SharedMemory(name=shm_name, create=True, size=frame_size, track=True)
        print(f"shm '{shm_name}' created.")
        return shm
    except FileExistsError:
        print(f"shm '{shm_name}' already exists.")
        shm = SharedMemory(name=shm_name)
        return shm
