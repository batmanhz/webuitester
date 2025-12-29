<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTestCaseStore } from '../stores/testCase'
import { useTestRunStore } from '../stores/testRun'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import { ElMessage } from 'element-plus'
import { Delete, Plus, VideoPlay } from '@element-plus/icons-vue'
import LogViewer from '../components/LogViewer.vue'

const route = useRoute()
const router = useRouter()
const store = useTestCaseStore()
const runStore = useTestRunStore()

const isNew = computed(() => route.params.id === 'new')
const loading = ref(false)
const currentRunId = ref<string | null>(null)

const form = ref({
  name: '',
  url: '',
  steps: [] as { instruction: string; expected_result: string; order: number }[]
})

onMounted(async () => {
  if (!isNew.value) {
    loading.value = true
    const id = route.params.id as string
    await store.fetchCase(id)
    if (store.currentCase) {
      form.value = {
        name: store.currentCase.name,
        url: store.currentCase.url,
        steps: store.currentCase.steps.map(s => ({
          instruction: s.instruction,
          expected_result: s.expected_result || '',
          order: s.order
        }))
      }
    }
    loading.value = false
  } else {
    // Add one empty step by default
    addStep()
  }
})

const addStep = () => {
  form.value.steps.push({
    instruction: '',
    expected_result: '',
    order: form.value.steps.length + 1
  })
}

const removeStep = (index: number) => {
  form.value.steps.splice(index, 1)
  // Reorder
  form.value.steps.forEach((step, idx) => {
    step.order = idx + 1
  })
}

const saveCase = async () => {
  if (!form.value.name || !form.value.url) {
    ElMessage.warning('Please fill in Name and Target URL')
    return
  }
  
  try {
    loading.value = true
    if (isNew.value) {
      const newCase = await store.createCase({
        name: form.value.name,
        url: form.value.url,
        steps: form.value.steps
      })
      ElMessage.success('Test case created successfully')
      // Redirect to edit mode of the new case so we can run it
      // Note: We use router.replace or router.push, but wait for it.
      // Also updating local form state if we want to stay on the page.
      // However, pushing to a new route might trigger onMounted again or not depending on reuse.
      // Since we key router-view by fullPath in App.vue, it should reload the component.
      await router.push(`/case/${newCase.id}`)
    } else {
      const caseId = route.params.id as string
      await store.updateCase(caseId, {
        name: form.value.name,
        url: form.value.url,
        steps: form.value.steps
      })
      ElMessage.success('Test case updated successfully')
    }
  } catch (e: any) {
    ElMessage.error(e.message || 'Failed to save test case')
  } finally {
    loading.value = false
  }
}

const runTest = async () => {
  if (isNew.value) {
    ElMessage.warning('Please save the test case first')
    return
  }
  
  const caseId = route.params.id as string
  try {
    const run = await runStore.createRun(caseId)
    currentRunId.value = run.id
    ElMessage.success('Test run started')
  } catch (e: any) {
    ElMessage.error('Failed to start run')
  }
}
</script>

<template>
  <div class="editor-view">
    <splitpanes class="default-theme" style="height: 100%">
      <pane min-size="20">
        <div class="panel-content left-panel">
          <div class="panel-header">
            <h2>{{ isNew ? 'New Test Case' : 'Edit Test Case' }}</h2>
            <div class="actions">
              <el-button type="primary" @click="saveCase" :loading="loading">Save</el-button>
              <el-button type="success" @click="runTest" :disabled="isNew">
                <el-icon><VideoPlay /></el-icon> Run
              </el-button>
            </div>
          </div>
          
          <el-form :model="form" label-position="top">
            <el-form-item label="Test Case Name" required>
              <el-input v-model="form.name" placeholder="e.g. Login Flow" />
            </el-form-item>
            
            <el-form-item label="Target URL" required>
              <el-input v-model="form.url" placeholder="https://example.com" />
            </el-form-item>
            
            <div class="steps-section">
              <div class="steps-header">
                <h3>Test Steps</h3>
                <el-button size="small" @click="addStep">
                  <el-icon><Plus /></el-icon> Add Step
                </el-button>
              </div>
              
              <div v-for="(step, index) in form.steps" :key="index" class="step-item">
                <div class="step-header">
                  <span class="step-number">#{{ index + 1 }}</span>
                  <el-button type="danger" link @click="removeStep(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="Instruction">
                      <el-input 
                        v-model="step.instruction" 
                        type="textarea" 
                        :rows="2"
                        placeholder="e.g. Click on 'Login' button" 
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Expected Result">
                      <el-input 
                        v-model="step.expected_result" 
                        type="textarea" 
                        :rows="2"
                        placeholder="e.g. Login modal appears" 
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-form>
        </div>
      </pane>
      <pane min-size="20">
        <div class="panel-content right-panel">
          <h2>Execution Feedback</h2>
           <LogViewer :runId="currentRunId" />
        </div>
      </pane>
    </splitpanes>
  </div>
</template>

<style scoped>
.editor-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-content {
  height: 100%;
  padding: 20px;
  background-color: #1e1e1e;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.right-panel {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.right-panel h2 {
  padding: 20px 20px 0 20px;
  margin-bottom: 10px;
}

.panel-header {
  display: flex;
  justify_content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-panel {
  border-right: 1px solid #333;
}

.steps-header {
  display: flex;
  justify_content: space-between;
  align-items: center;
  margin: 20px 0 10px;
  border-bottom: 1px solid #333;
  padding-bottom: 10px;
}

.step-item {
  background-color: #252525;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #333;
}

.step-header {
  display: flex;
  justify_content: space-between;
  margin-bottom: 10px;
}

.step-number {
  font-weight: bold;
  color: #888;
}

/* Splitpanes Theme Overrides */
:deep(.splitpanes__splitter) {
  background-color: #333 !important;
  width: 4px;
}
</style>
