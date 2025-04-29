import logging
import sys

from aiortc import RTCPeerConnection, RTCSessionDescription
from anyio.from_thread import start_blocking_portal
from pydantic import BaseModel
from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory, Commands, )
from pytauri.webview import WebviewWindow

from pytauri_vue_starter.customvideostreamtrack import CustomVideoStreamTrack

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

commands: Commands = Commands()


class RTCModel(BaseModel):
    sdp: str
    type: str


pc: RTCPeerConnection | None = None


@commands.command()
async def socket(body: bytes) -> RTCModel:
    global pc
    camera_name = 0

    logger.info("WebSocket connection accepted")

    pc = RTCPeerConnection()

    logger.info(f"Creating video track with camera name: {camera_name}")

    video_sender = CustomVideoStreamTrack(camera_name)
    pc.addTrack(video_sender)

    @pc.on("datachannel")
    def on_datachannel(channel):
        logger.info(f"Data channel established: {channel.label}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "connected":
            logger.info("WebRTC connection established successfully")
        elif pc.connectionState == "failed":
            logger.error("WebRTC connection failed")

    logger.info("Creating offer")
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    return RTCModel(sdp=offer.sdp, type=offer.type)


@commands.command()
async def socket2(body: RTCModel, webview_window: WebviewWindow) -> bytes:
    global pc
    logger.info(f"Received answer from client: {body}")

    answer = RTCSessionDescription(
        sdp=body.sdp, type=body.type
    )
    await pc.setRemoteDescription(answer)
    logger.info("Remote description set successfully")

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
