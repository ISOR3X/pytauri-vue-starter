<script setup lang="ts">

import {onMounted, onUnmounted, ref, useTemplateRef} from "vue";
import {pyInvoke} from "tauri-plugin-pytauri-api";


let pc: RTCPeerConnection | undefined = undefined;

const videoElement = useTemplateRef<HTMLVideoElement>('video')
const streamState = ref('CLOSED')


onMounted(async () => {
  start();

  const mod = await pyInvoke<RTCSessionDescriptionInit>("socket", {})

  if (pc == undefined) {
    console.log("No peer connection");
    return
  }

  await pc.setRemoteDescription({sdp: mod.sdp, type: mod.type});

  console.log("Remote description set successfully");

  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);

  await pyInvoke("socket2", {
    sdp: answer.sdp,
    type: answer.type
  });

  console.log("Answer sent to server");
})

onUnmounted(() => {
  stop()
})

function createPeerConnection() {
  console.log('Creating peer connection');
  const config = {
    sdpSemantics: 'unified-plan',
    iceServers: [{urls: ['stun:stun.l.google.com:19302']}]
  };

  pc = new RTCPeerConnection(config);

  pc.addEventListener('track', function (evt) {
    console.log('Track event:', evt);
    if (evt.track.kind === 'video') {
      console.log('Video track received, setting as source');

      if (!evt.streams[0]) {
        console.error('No stream found in track event');
        return;
      }
      videoElement.value!.srcObject = evt.streams[0];

      videoElement.value!.onloadedmetadata = function () {
        console.log('Video metadata loaded, video dimensions:', videoElement.value!.videoWidth, 'x', videoElement.value!.videoHeight);
      };

      videoElement.value!.onplay = function () {
        console.log('Video playback started');
        streamState.value = 'OPEN';
      };

      videoElement.value!.onerror = function (e) {
        console.error('Video error:', e);
      };
    }
  });

  return pc;
}

function start() {
  streamState.value = 'CONNECTING';
  pc = createPeerConnection();
}

function stop() {
  if (videoElement.value && videoElement.value.srcObject) {
    (videoElement.value.srcObject as MediaStream).getTracks().forEach(track => track.stop());
    videoElement.value.srcObject = null;
  }

  // close transceivers
  if (pc && pc.getTransceivers) {
    pc.getTransceivers().forEach(function (transceiver) {
      if (transceiver.stop) {
        transceiver.stop();
      }
    });
  }

  // close local audio / video
  if (pc) {
    console.log('Closing peer connection');
    streamState.value = 'CLOSED';
    pc.getSenders().forEach(function (sender) {
      if (sender.track) {
        sender.track.stop();
      }
    });

    // close peer connection
    setTimeout(function () {
      if (pc == null) {
        return;
      }
      pc.close();
      pc = undefined;
    }, 500);
  }
}
</script>

<template>
  <video ref="video" autoplay playsinline style="background-color: #6bae75;"/>
</template>

<style scoped>

</style>