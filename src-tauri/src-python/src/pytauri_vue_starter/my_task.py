import asyncio
import json

from pydantic import RootModel
from pytauri import ImplManager, Emitter, Listener, Event


class MyTask:
    def __init__(self, name: str, impl_manager: ImplManager = None):
        self.name = name
        self.impl_manager = impl_manager

    def log(self, msg: str):
        payload = RootModel[str](msg)
        Emitter.emit(self.impl_manager, "log", payload)
        print(msg)

    async def confirm(self, msg: str) -> bool:
        payload = RootModel[str](msg)
        payload_resp: dict = None

        Emitter.emit(self.impl_manager, "confirm", payload)

        response_flag = asyncio.Event()

        def handle_resp(event: Event, _loop):
            nonlocal response_flag
            nonlocal payload_resp
            payload_resp = json.loads(event.payload)
            _loop.call_soon_threadsafe(response_flag.set)

        loop = asyncio.get_running_loop()
        Listener.once(self.impl_manager, "confirm-response", lambda e: handle_resp(e, loop))
        await response_flag.wait()
        return payload_resp["response"]

    async def run(self):
        self.log(f'Starting {self.name}')
        try:
            for i in range(50):
                await asyncio.sleep(1)
                self.log(f'Hello from {self.name}')
                if (i % 5) == 0:
                    resp = await self.confirm(f'Do you want to continue? {i}')
                    self.log(f'Response: {resp}')
        except asyncio.CancelledError:
            self.log(f'Cancelled {self.name}')
        finally:
            self.log(f'Finished {self.name}')
