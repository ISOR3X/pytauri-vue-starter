import asyncio
import logging
import sys
import time

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from anyio.from_thread import start_blocking_portal
from pydantic import BaseModel
from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory, Commands, )

from pytauri_vue_starter.video_controller.consumer_track import ConsumerTrack
from pytauri_vue_starter.video_controller.producer_process import VideoProducerProcess

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

commands: Commands = Commands()


class RTCModel(BaseModel):
    sdp: str
    type: str


relay = None
webcam = None
pcs: set[RTCPeerConnection] = set()


def create_local_tracks():
    global relay, webcam

    if relay is None:
        webcam = ConsumerTrack()
        relay = MediaRelay()
    return None, relay.subscribe(webcam)


@commands.command()
async def offer(body: RTCModel) -> RTCModel:
    _offer = RTCSessionDescription(sdp=body.sdp, type=body.type)

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # open media source
    _, video = create_local_tracks()

    if video:
        pc.addTrack(video)

    await pc.setRemoteDescription(_offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return RTCModel(sdp=pc.localDescription.sdp, type=pc.localDescription.type)


@commands.command()
async def on_shutdown() -> bytes:
    # close RTC peer connections
    rtc_close_calls = [pc.close() for pc in pcs]
    await asyncio.gather(*rtc_close_calls)
    pcs.clear()
    return b"null"


def main():
    vpp = VideoProducerProcess(
        camera_name="video=HP HD Camera",
        framerate=30,
        resolution=(1280, 720)
    )

    try:
        vpp.start()

        with start_blocking_portal("asyncio") as portal:
            builder = builder_factory()
            app = builder.build(
                BuilderArgs(
                    context_factory(),
                    invoke_handler=commands.generate_handler(portal),
                )
            )
            app.run()
    finally:
        vpp.terminate()
