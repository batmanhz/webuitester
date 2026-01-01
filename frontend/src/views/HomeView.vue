<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTestCaseStore } from '../stores/testCase'
import { storeToRefs } from 'pinia'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useTestCaseStore()
const { cases, loading } = storeToRefs(store)

const showIntentDialog = ref(false)
const generating = ref(false)
const intentForm = ref({
  url: '',
  intent: ''
})

const loadData = () => {
  store.fetchCases()
}

onMounted(() => {
  loadData()
})

const openNewCaseDialog = () => {
  intentForm.value = { url: '', intent: '' }
  showIntentDialog.value = true
}

const handleGenerate = async () => {
  if (!intentForm.value.url || !intentForm.value.intent) {
    ElMessage.warning('Please fill in both URL and Intent')
    return
  }

  generating.value = true
  try {
    const generated = await store.generateSteps({
      url: intentForm.value.url,
      intent: intentForm.value.intent
    })
    
    // Store generated data in store state or pass via router
    // Here we pass via query params or state. 
    // Since steps are complex objects, query params are limited.
    // Better to use a transient store state or just navigate to 'new' and have 'new' read from a shared state.
    // For simplicity, let's use the store's currentCase as a temporary holder or add a 'draft' state.
    // Or we can modify EditorView to handle a special 'generated' prop.
    // Let's use localStorage or Pinia state. Pinia is better.
    // We will update store.currentCase with the generated data (without ID) and then navigate.
    
    store.currentCase = {
      id: '', // Empty ID signifies new
      name: generated.name,
      url: intentForm.value.url,
      steps: generated.steps.map((s, idx) => ({ ...s, order: idx + 1, id: undefined, expected_result: s.expected_result || null }))
    }
    
    showIntentDialog.value = false
    router.push('/case/new?mode=generated')
  } catch (e: any) {
    ElMessage.error(e.message || 'Failed to generate steps')
  } finally {
    generating.value = false
  }
}

const openCase = (id: string) => {
  router.push(`/case/${id}`)
}

const deleteCase = async (id: string) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this test case?',
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    await store.deleteCase(id)
    ElMessage.success('Test case deleted')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || 'Failed to delete test case')
    }
  }
}
</script>

<template>
  <div class="home-view">
    <div class="header">
      <h1>Test Cases</h1>
      <el-button type="primary" @click="openNewCaseDialog">
        <el-icon><Plus /></el-icon> New Case
      </el-button>
    </div>
    
    <div v-if="loading && !generating" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="cases.length === 0" class="empty-state">
      <el-empty description="No test cases found" />
    </div>
    
    <div v-else class="case-list">
      <el-table :data="cases" style="width: 100%" @row-click="row => openCase(row.id)">
        <el-table-column prop="name" label="Name" />
        <el-table-column prop="url" label="Target URL" />
        <el-table-column prop="created_at" label="Created At" />
        <el-table-column fixed="right" label="Operations" width="150">
          <template #default="scope">
            <el-button link type="primary" size="small" @click.stop="openCase(scope.row.id)">
              Edit
            </el-button>
            <el-button link type="danger" size="small" @click.stop="deleteCase(scope.row.id)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Intent Dialog -->
    <el-dialog
      v-model="showIntentDialog"
      title="Create New Test Case"
      width="50%"
      :close-on-click-modal="!generating"
    >
      <el-form :model="intentForm" label-position="top">
        <el-form-item label="Target URL" required>
          <el-input v-model="intentForm.url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="Test Intent" required>
          <el-input
            v-model="intentForm.intent"
            type="textarea"
            :rows="4"
            placeholder="Describe what you want to test... e.g., 'Login with admin/123456 and verify dashboard loads'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showIntentDialog = false" :disabled="generating">Cancel</el-button>
          <el-button type="primary" @click="handleGenerate" :loading="generating">
            <el-icon><MagicStick /></el-icon> Generate Steps
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.home-view {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.case-list {
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 10px;
}
</style>
