import asyncio

from pytauri import ImplManager, Emitter


class MyTask:
    def __init__(self, name: str, impl_manager: ImplManager = None):
        self.name = name
        self.impl_manager = impl_manager

    def log(self, msg: str):
        Emitter.emit_str(self.impl_manager, "log", msg)
        print(msg)

    async def run(self):
        for i in range(10):
            await asyncio.sleep(1)
            self.log(f'Hello from {self.name}')
