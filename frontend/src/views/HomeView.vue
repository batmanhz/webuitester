<script setup lang="ts">
import { onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { useTestCaseStore } from '../stores/testCase'
import { storeToRefs } from 'pinia'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useTestCaseStore()
const { cases, loading } = storeToRefs(store)

const loadData = () => {
  store.fetchCases()
}

onMounted(() => {
  loadData()
})

// Since we are using router view which might be cached or reused, 
// we want to ensure list is fresh when navigating back.
// But Standard Vue Router navigation usually remounts unless keep-alive is used.
// Let's rely on onMounted, but ensure fetchCases actually fetches fresh data.

const createCase = () => {
  router.push('/case/new')
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
      <el-button type="primary" @click="createCase">
        <el-icon><Plus /></el-icon> New Case
      </el-button>
    </div>
    
    <div v-if="loading" class="loading-state">
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
  </div>
</template>

<style scoped>
.home-view {
  padding: 20px;
}

.header {
  display: flex;
  justify_content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
