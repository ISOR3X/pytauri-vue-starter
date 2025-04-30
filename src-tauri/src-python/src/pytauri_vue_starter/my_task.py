import asyncio

from pydantic import RootModel
from pytauri import ImplManager, Emitter


class MyTask:
    def __init__(self, name: str, impl_manager: ImplManager = None):
        self.name = name
        self.impl_manager = impl_manager

    def log(self, msg: str):
        payload = RootModel[str](msg)
        Emitter.emit(self.impl_manager, "log", payload)
        print(msg)

    async def run(self):
        self.log(f'Starting {self.name}')
        try:
            for i in range(50):
                await asyncio.sleep(1)
                self.log(f'Hello from {self.name}')
        except asyncio.CancelledError:
            self.log(f'Cancelled {self.name}')
        finally:
            self.log(f'Finished {self.name}')
