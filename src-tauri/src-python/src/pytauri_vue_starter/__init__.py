from multiprocessing import Process

import cv2
from anyio.from_thread import start_blocking_portal
from pydantic import RootModel
from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory, Commands,
)
from pytauri.ffi.webview import WebviewWindow
from pytauri.ipc import Channel, JavaScriptChannelId

from pytauri_vue_starter.frame_controller import FrameProducer, FrameConsumer

commands: Commands = Commands()

Msg = RootModel[str]


@commands.command()
async def start_stream(
        body: JavaScriptChannelId[Msg], webview_window: WebviewWindow
) -> bytes:
    channel: Channel[Msg] = body.channel_on(webview_window.as_ref_webview())
    fc = FrameConsumer(["top"])

    try:
        while True:
            f = fc.read_frame(resolution=(1920 // 2, 1080 // 2))

            _, buffer = cv2.imencode(".png", f)
            image_data = buffer.tobytes()

            channel.send(image_data)
    finally:
        return b"null"


def producer(**kwargs: int):
    frame_producer = FrameProducer(kwargs)
    frame_producer.start()


def main():
    fp_process = Process(target=producer, kwargs={'top': 0})

    with start_blocking_portal("asyncio") as portal:

        try:
            fp_process.start()

            builder = builder_factory()
            app = builder.build(
                BuilderArgs(
                    context_factory(),
                    invoke_handler=commands.generate_handler(portal),
                )
            )
            app.run()
        finally:
            fp_process.terminate()
            print("Frame producer process terminated.")
