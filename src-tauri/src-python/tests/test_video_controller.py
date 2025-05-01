import asyncio
import time

import cv2
import numpy
from aiortc.contrib.media import MediaPlayer
from av import VideoFrame

from pytauri_vue_starter.video_controller.consumer_thread import VideoConsumerThread
from pytauri_vue_starter.video_controller.producer_thread import VideoProducerThread


async def main():
    vpp = VideoProducerThread(
        camera_name="video=HP HD Camera",
        framerate=30,
        resolution=(1280, 720)
    )

    vpp.start()
    time.sleep(2)

    vcp = VideoConsumerThread(resolution=(1280,720))
    vcp.start()

    vcp.join(timeout=10)


async def standalone_media_player():
    try:
        mp = MediaPlayer("video=HP HD Camera", format="dshow", options={"framerate": "30", "video_size": "1280x720"})

    except Exception as e:
        print(f"Error opening video source: {e}")
        print("Check if the camera name 'HP HD Camera' is correct or try using index '0'.")
        return

    print("Press 'q' in the video window to quit.")
    while True:
        try:
            frame = await mp.video.recv()
            assert isinstance(frame, VideoFrame)
            frame_array = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

            cv2.imshow("Video Consumer", frame_array)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error receiving or processing frame: {e}")
            break  # Exit loop on error

    # Release resources
    if mp and mp.video:
        mp.video.stop()
    cv2.destroyAllWindows()
    print("Video stream stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        # Ensure windows are closed even if interrupted
        cv2.destroyAllWindows()
