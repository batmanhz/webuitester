import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface TestRun {
  id: string
  case_id: string
  status: string
  logs: any[]
  created_at: string
}

export const useTestRunStore = defineStore('testRun', () => {
  const currentRun = ref<TestRun | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const createRun = async (caseId: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/runs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ case_id: caseId }),
      })
      if (!response.ok) throw new Error('Failed to start test run')
      currentRun.value = await response.json()
      return currentRun.value
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    currentRun,
    loading,
    error,
    createRun
  }
})
