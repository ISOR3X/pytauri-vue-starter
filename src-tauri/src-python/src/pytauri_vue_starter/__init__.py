import asyncio
import logging
import platform
import sys

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay, MediaPlayer
from anyio.from_thread import start_blocking_portal
from pydantic import BaseModel
from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory, Commands, )

from pytauri_vue_starter.customvideostreamtrack import CustomVideoStreamTrack

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

    options = {"framerate": "30", "video_size": "640x480"}
    if relay is None:
        if platform.system() == "Darwin":
            webcam = MediaPlayer(
                "default:none", format="avfoundation", options=options
            )
        elif platform.system() == "Windows":
            webcam = MediaPlayer(
                "video=HP HD Camera", format="dshow", options=options
            )
        else:
            webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
        relay = MediaRelay()
    return None, relay.subscribe(webcam.video)


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
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    return b"null"


def main():
    with start_blocking_portal("asyncio") as portal:
        builder = builder_factory()
        app = builder.build(
            BuilderArgs(
                context_factory(),
                # 👇
                invoke_handler=commands.generate_handler(portal),
            )
        )
        app.run()
