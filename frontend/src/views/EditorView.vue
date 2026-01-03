<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTestCaseStore } from '../stores/testCase'
import { useTestRunStore } from '../stores/testRun'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import { ElMessage } from 'element-plus'
import { Delete, Plus, VideoPlay, Rank } from '@element-plus/icons-vue'
import LogViewer from '../components/LogViewer.vue'
import draggable from 'vuedraggable'

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

// Watch steps changes to update order
watch(() => form.value.steps, (newSteps) => {
    newSteps.forEach((step, index) => {
        step.order = index + 1
    })
}, { deep: true })

onMounted(async () => {
  if (!isNew.value) {
    // Edit Mode
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
    // New Case Mode
    // Check if we have generated data in store (passed from HomeView)
    if (store.currentCase && !store.currentCase.id) {
        form.value = {
            name: store.currentCase.name,
            url: store.currentCase.url,
            steps: store.currentCase.steps.map(s => ({
                instruction: s.instruction,
                expected_result: s.expected_result || '',
                order: s.order
            }))
        }
        // Clear temp data
        store.currentCase = null
    } else {
        // Fallback or fresh start
        addStep()
    }
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
}

const saveCase = async (andRun: boolean = false) => {
  if (!form.value.name || !form.value.url) {
    ElMessage.warning('Please fill in Name and Target URL')
    return
  }
  
  try {
    loading.value = true
    let caseId = ''
    if (isNew.value) {
      const newCase = await store.createCase({
        name: form.value.name,
        url: form.value.url,
        steps: form.value.steps
      })
      ElMessage.success('Test case created successfully')
      caseId = newCase.id
      // Navigate to real ID URL
      await router.push(`/case/${caseId}`)
    } else {
      caseId = route.params.id as string
      await store.updateCase(caseId, {
        name: form.value.name,
        url: form.value.url,
        steps: form.value.steps
      })
      ElMessage.success('Test case updated successfully')
    }

    if (andRun) {
        await runTest(caseId)
    }

  } catch (e: any) {
    ElMessage.error(e.message || 'Failed to save test case')
  } finally {
    loading.value = false
  }
}

const runTest = async (id?: string) => {
  const caseId = id || (route.params.id as string)
  
  if (isNew.value && !id) {
     // Should assume saveCase(true) handles this
    ElMessage.warning('Please save the test case first')
    return
  }
  
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
      <pane min-size="40">
        <div class="panel-content left-panel">
          <div class="panel-header">
            <!-- Left: Title -->
            <h2>{{ isNew ? 'New Test Case' : 'Edit Test Case' }}</h2>
            
            <!-- Right: Actions -->
            <div class="actions">
              <el-button @click="saveCase(false)" :loading="loading">Save Only</el-button>
              <el-button type="primary" @click="saveCase(true)" :loading="loading">
                <el-icon><VideoPlay /></el-icon> Save & Run
              </el-button>
            </div>
          </div>
          
          <el-form :model="form" label-position="top">
            <!-- Full Width Inputs -->
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
              
              <draggable 
                v-model="form.steps" 
                item-key="order"
                handle=".drag-handle"
                :animation="200"
              >
                <template #item="{ element, index }">
                  <div class="step-item">
                    <div class="step-header">
                      <div class="step-title">
                        <el-icon class="drag-handle" style="cursor: move; margin-right: 10px"><Rank /></el-icon>
                        <span class="step-number">#{{ index + 1 }}</span>
                      </div>
                      <el-button type="danger" link @click="removeStep(index)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                    
                    <el-row :gutter="20">
                      <el-col :span="12">
                        <el-form-item label="Instruction">
                          <el-input 
                            v-model="element.instruction" 
                            type="textarea" 
                            :rows="4"
                            placeholder="e.g. Click on 'Login' button" 
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="12">
                        <el-form-item label="Expected Result">
                          <el-input 
                            v-model="element.expected_result" 
                            type="textarea" 
                            :rows="4"
                            placeholder="e.g. Login modal appears" 
                          />
                        </el-form-item>
                      </el-col>
                    </el-row>
                  </div>
                </template>
              </draggable>
            </div>
          </el-form>
        </div>
      </pane>
      <pane min-size="40">
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
  padding: 40px;
  overflow-y: auto;
  box-sizing: border-box;
}

/* Ensure form items take full width */
.el-form-item {
  width: 100%;
}

.left-panel {
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  /* Increase padding for wider feel */
  padding: 40px 60px; 
}

.right-panel {
  background-color: #1e1e1e;
  color: #fff;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.right-panel > h2 {
    padding: 20px 40px 0 40px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.actions {
  display: flex;
  gap: 15px; /* Separate buttons */
}


.steps-section {
  margin-top: 30px;
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.step-item {
  background: var(--el-fill-color-light);
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid var(--el-border-color-lighter);
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.step-title {
    display: flex;
    align-items: center;
}

.step-number {
  font-weight: bold;
  color: var(--el-color-info);
}

.drag-handle:hover {
    color: var(--el-color-primary);
}
</style>
