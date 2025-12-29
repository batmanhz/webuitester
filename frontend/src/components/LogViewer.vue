<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'

const props = defineProps<{
  runId: string | null
}>()

const logs = ref<{type: string, data: any, timestamp?: string}[]>([])
const currentScreenshot = ref<string | null>(null)
const status = ref<string>('IDLE')
let socket: WebSocket | null = null

const connect = () => {
  if (!props.runId) return
  
  // Close existing
  if (socket) socket.close()
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host // includes port if dev
  // In dev, vite proxy forwards /api to backend 19000. 
  // But WS proxying might be tricky with Vite.
  // Ideally, if we configured vite proxy correctly:
  // '/api/runs/ws' -> 'ws://localhost:19000/api/runs/ws'
  // Let's try relative path with ws protocol replacement?
  // Actually, standard practice with Vite proxy:
  // If we use `ws://localhost:5173/api/runs/ws/...` vite should proxy it.
  
  const wsUrl = `${protocol}//${host}/api/runs/ws/${props.runId}`
  
  console.log('Connecting to WS:', wsUrl)
  socket = new WebSocket(wsUrl)
  
  socket.onopen = () => {
    logs.value.push({ type: 'info', data: 'Connected to log stream' })
  }
  
  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      // msg structure: { type: '...', data: ... }
      
      if (msg.type === 'screenshot') {
        currentScreenshot.value = `data:image/jpeg;base64,${msg.data}`
      } else if (msg.type === 'status') {
        status.value = msg.data
        logs.value.push({ type: 'status', data: `Status changed to ${msg.data}` })
      } else {
        // Log, step_start, step_end, etc.
        logs.value.push(msg)
      }
      
      scrollToBottom()
    } catch (e) {
      console.error('Failed to parse WS message', e)
    }
  }
  
  socket.onclose = () => {
    logs.value.push({ type: 'info', data: 'Connection closed' })
  }
  
  socket.onerror = (e) => {
    console.error('WS Error', e)
    logs.value.push({ type: 'error', data: 'WebSocket connection error' })
  }
}

const logContainer = ref<HTMLElement | null>(null)
const scrollToBottom = async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

watch(() => props.runId, (newId) => {
  if (newId) {
    logs.value = []
    currentScreenshot.value = null
    status.value = 'PENDING'
    connect()
  }
})

onUnmounted(() => {
  if (socket) socket.close()
})

defineExpose({
  logs,
  status
})
</script>

<template>
  <div class="log-viewer">
    <div class="screenshot-pane">
      <div v-if="currentScreenshot" class="screenshot-container">
        <img :src="currentScreenshot" alt="Current View" />
      </div>
      <div v-else class="placeholder">
        <el-icon class="icon"><Monitor /></el-icon>
        <span>Waiting for execution...</span>
      </div>
    </div>
    
    <div class="logs-pane" ref="logContainer">
      <div v-for="(log, idx) in logs" :key="idx" class="log-entry" :class="log.type">
        <span class="timestamp" v-if="log.timestamp">{{ log.timestamp }}</span>
        <span class="type">[{{ log.type.toUpperCase() }}]</span>
        <span class="message">{{ typeof log.data === 'string' ? log.data : JSON.stringify(log.data) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.log-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #1e1e1e;
  color: #d4d4d4;
}

.screenshot-pane {
  flex: 1;
  background-color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-bottom: 1px solid #333;
  min-height: 200px;
}

.screenshot-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666;
  gap: 10px;
}

.logs-pane {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background-color: #1e1e1e;
}

.log-entry {
  margin-bottom: 4px;
  word-break: break-all;
  white-space: pre-wrap;
  text-align: left;
}

.log-entry.error { color: #f48771; }
.log-entry.info { color: #6a9955; }
.log-entry.step_start { color: #569cd6; font-weight: bold; margin-top: 8px; }
.log-entry.step_end { color: #569cd6; margin-bottom: 8px; }
.log-entry.status { color: #c586c0; font-style: italic; }

.type {
  margin-right: 8px;
  opacity: 0.7;
}
</style>
