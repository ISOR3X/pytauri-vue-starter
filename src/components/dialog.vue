<script setup lang="ts">
import {getCurrentWebviewWindow} from "@tauri-apps/api/webviewWindow";
import {onMounted} from "vue";
import {emit} from "@tauri-apps/api/event";
import {ask} from '@tauri-apps/plugin-dialog';

const appWebview = getCurrentWebviewWindow();
onMounted(async () => {
  await appWebview.listen<string>('confirm', async (event) => {
    const answer = await ask(event.payload, {
      title: 'Tauri',
      kind: 'warning',
    });
    await emit('confirm-response', {response: answer});
  });
})
</script>

<template>

</template>

<style scoped>

</style>