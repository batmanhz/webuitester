<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'
import { useTestRunStore } from '../stores/testRun'
import { VideoPause } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  runId: string | null
}>()

const runStore = useTestRunStore()

const logs = ref<{type: string, data: any, timestamp?: string}[]>([])
const currentScreenshot = ref<string | null>(null)
const status = ref<string>('IDLE')
let socket: WebSocket | null = null
const stopping = ref(false)

const connect = () => {
  if (!props.runId) return
  
  // Close existing
  if (socket) socket.close()
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host // includes port if dev
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

const handleStop = async () => {
    if (!props.runId) return
    stopping.value = true
    try {
        await runStore.stopRun(props.runId)
        ElMessage.info('Stop signal sent')
    } catch (e: any) {
        ElMessage.error(e.message || 'Failed to stop run')
    } finally {
        stopping.value = false
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
        <div class="status-bar">
            <el-tag :type="status === 'RUNNING' ? 'success' : status === 'FAILED' ? 'danger' : 'info'">
                Status: {{ status }}
            </el-tag>
            <el-button 
                v-if="status === 'RUNNING'" 
                type="danger" 
                size="small" 
                @click="handleStop"
                :loading="stopping"
            >
                <el-icon><VideoPause /></el-icon> Stop
            </el-button>
        </div>

      <div v-if="currentScreenshot" class="screenshot-container">
        <img :src="currentScreenshot" alt="Current View" />
      </div>
      <div v-else class="placeholder">
        <p>Waiting for execution...</p>
      </div>
    </div>
    
    <div class="console-pane" ref="logContainer">
      <div v-for="(log, idx) in logs" :key="idx" class="log-line" :class="log.type">
        <span class="timestamp" v-if="log.timestamp">[{{ log.timestamp }}]</span>
        <span class="content">
            <template v-if="log.type === 'status'">
                STATUS: {{ log.data }}
            </template>
             <template v-else-if="typeof log.data === 'object'">
                {{ JSON.stringify(log.data) }}
            </template>
            <template v-else>
                {{ log.data }}
            </template>
        </span>
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
  border-left: 1px solid #333;
}

.screenshot-pane {
  flex: 1; /* Takes 60% ideally, but flex 1 and console fixed height is easier */
  height: 60%;
  border-bottom: 1px solid #333;
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: #000;
  overflow: hidden;
}

.status-bar {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 10;
    display: flex;
    gap: 10px;
}

.screenshot-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.screenshot-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #666;
}

.console-pane {
  height: 40%;
  overflow-y: auto;
  padding: 10px;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  background-color: #1e1e1e;
}

.log-line {
  margin-bottom: 4px;
  line-height: 1.4;
  word-break: break-all;
  color: #d4d4d4;
}

.log-line.error { color: #f87171; }
.log-line.status { color: #60a5fa; font-weight: bold; }
.log-line.info { color: #9ca3af; }

/* Custom scrollbar */
.console-pane::-webkit-scrollbar {
  width: 8px;
}
.console-pane::-webkit-scrollbar-track {
  background: #1e1e1e;
}
.console-pane::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}
</style>
