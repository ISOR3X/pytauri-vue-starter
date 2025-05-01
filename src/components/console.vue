<script setup lang="ts">
import {getCurrentWebviewWindow} from "@tauri-apps/api/webviewWindow";
import {nextTick, onMounted, ref} from "vue";

const messages = ref<string[]>([]);
const messageContainer = ref<HTMLElement | null>(null);

const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
    }
  });
};

const appWebview = getCurrentWebviewWindow();
onMounted(async () => {
  await appWebview.listen<string>('log', (event) => {
    messages.value.push(event.payload);
    // Keep only the latest 100 messages
    if (messages.value.length > 100) {
      messages.value = messages.value.slice(-100);
    }
    scrollToBottom();
  });
})
</script>

<template>
  <div class="console-container">
    <ul ref="messageContainer" v-bind="$attrs">
      <li v-for="m in messages" key="m">{{ m }}</li>
    </ul>
  </div>
</template>

<style>

</style>

<style scoped>
.console-container {
  display: flex;
  flex-direction: column;
  min-height: 100px;
  background-color: color-mix(in oklch, transparent, black 20%);
  padding: 0.5rem 0 0.5rem 0.5rem;
  box-sizing: border-box;
}

ul {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: color-mix(in oklch, transparent, white 50%) transparent;
  margin: 0;
  padding: 0 0.5rem 0 0;
  //height: 100%;
  box-sizing: border-box;
}

li {
  list-style: none;
  text-align: left;
}
</style>
