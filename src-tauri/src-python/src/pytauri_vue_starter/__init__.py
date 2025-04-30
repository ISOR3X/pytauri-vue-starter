import asyncio
from typing import Optional

from anyio.from_thread import start_blocking_portal
from pytauri import (
    BuilderArgs,
    Commands, builder_factory, context_factory,
)
from pytauri.ipc import InvokeException
from pytauri.webview import WebviewWindow

from pytauri_vue_starter.my_task import MyTask

commands: Commands = Commands()

_background_task: Optional[asyncio.Task[None]] = None


@commands.command()
async def start_task(
        body: bytes, webview_window: WebviewWindow
) -> bytes:
    global _background_task

    if _background_task is not None:
        raise InvokeException("Background task already running")

    task = MyTask("background task", webview_window)
    _background_task = asyncio.create_task(task.run())
    return b"null"


@commands.command()
async def stop_task(body: bytes) -> bytes:
    global _background_task

    if _background_task is None:
        raise InvokeException("Background task not running")

    _background_task.cancel()
    _background_task = None
    return b"null"


def main():
    with start_blocking_portal("asyncio") as portal:
        app = builder_factory().build(
            BuilderArgs(
                context=context_factory(),
                invoke_handler=commands.generate_handler(portal),
            )
        )
        app.run()
