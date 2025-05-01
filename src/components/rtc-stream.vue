<script setup lang="ts">

import {ref, useTemplateRef} from "vue";
import {pyInvoke} from "tauri-plugin-pytauri-api";

let pc: RTCPeerConnection | null = null;
const video = useTemplateRef<HTMLVideoElement>("video");
const checked = ref(false);

function negotiate() {
  if (pc == null) return;
  pc.addTransceiver('video', {direction: 'recvonly'});
  pc.addTransceiver('audio', {direction: 'recvonly'});
  return pc.createOffer().then((offer) => {
    return pc!.setLocalDescription(offer);
  }).then(() => {
    // wait for ICE gathering to complete
    return new Promise((resolve) => {
      if (pc!.iceGatheringState === 'complete') {
        resolve(null);
      } else {
        const checkState = () => {
          if (pc!.iceGatheringState === 'complete') {
            pc!.removeEventListener('icegatheringstatechange', checkState);
            resolve(null);
          }
        };
        pc!.addEventListener('icegatheringstatechange', checkState);
      }
    });
  }).then(() => {
    const offer = pc!.localDescription;
    return pyInvoke<RTCSessionDescriptionInit>('offer', {
      sdp: offer!.sdp,
      type: offer!.type
    });
  }).then((response) => {
    return response;
  }).then((answer) => {
    return pc!.setRemoteDescription(answer);
  }).catch((e) => {
    alert(e);
  });
}

function start() {
  const config: any = {
    sdpSemantics: 'unified-plan'
  };

  if (checked) {
    config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
  }

  pc = new RTCPeerConnection(config);

  // connect audio / video
  pc.addEventListener('track', (evt) => {
    if (evt.track.kind == 'video') {
      video.value!.srcObject = evt.streams[0];
    } else {
    }
  });


  negotiate();

}

function stop() {
  // close peer connection
  setTimeout(() => {
    pc!.close();
  }, 500);
}

</script>

<template>
  <div class="control-container">
    <button @click="start">start</button>
    <button @click="stop">stop</button>
    <span><input v-model="checked" type="checkbox">Use STUN</span>
  </div>
  <video ref="video" autoplay playsinline/>
</template>

<style scoped>

video {
  object-fit: contain;
  flex-grow: 1;
  flex-shrink: 1;
  height: 10rem;
  margin-bottom: 1rem;
}

.control-container {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: center;
}
</style>