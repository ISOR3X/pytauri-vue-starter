<script setup lang="ts">
import {onBeforeUnmount, onMounted, ref} from "vue";
import {Channel, pyInvoke} from "tauri-plugin-pytauri-api";

const imageUrl = ref("");

onMounted(async () => {
  console.log("mounted");
  const channel = new Channel<ArrayBuffer>();
  channel.onmessage = (msg) => {
    if (imageUrl.value) {
      URL.revokeObjectURL(imageUrl.value);
    }

    const blob = new Blob([msg], {type: 'image/png'});

    imageUrl.value = URL.createObjectURL(blob);
  };
  await pyInvoke("start_stream", channel);
})

onBeforeUnmount(() => {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value);
  }
})

</script>

<template>
  <div>
    <img :src="imageUrl" alt="img" v-bind="$attrs"/>
  </div>
</template>

<style scoped>
div {
  margin-inline: auto;
  width: 100%;
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;

  img {
    aspect-ratio: 16/9;
    max-height: 100%;
    width: 100%;
    object-fit: contain;
    margin: 0 auto;
  }
}


</style>
