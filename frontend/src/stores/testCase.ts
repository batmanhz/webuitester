import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Ref } from 'vue'

export interface TestStep {
  id?: string
  instruction: string
  expected_result: string | null
  order: number
}

export interface TestCase {
  id: string
  name: string
  url: string
  created_at?: string
  steps: TestStep[]
}

export interface TestCaseCreate {
  name: string
  url: string
  steps: Omit<TestStep, 'id'>[]
}

export const useTestCaseStore = defineStore('testCase', () => {
  const cases: Ref<TestCase[]> = ref([])
  const currentCase: Ref<TestCase | null> = ref(null)
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchCases = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/cases')
      if (!response.ok) throw new Error('Failed to fetch test cases')
      cases.value = await response.json()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const fetchCase = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/cases/${id}`)
      if (!response.ok) throw new Error('Failed to fetch test case')
      currentCase.value = await response.json()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const createCase = async (caseData: TestCaseCreate) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/cases', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(caseData),
      })
      if (!response.ok) throw new Error('Failed to create test case')
      const newCase = await response.json()
      cases.value.push(newCase)
      return newCase
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateCase = async (id: string, caseData: TestCaseCreate) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/cases/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(caseData),
      })
      if (!response.ok) throw new Error('Failed to update test case')
      const updatedCase = await response.json()
      
      // Update local state
      const index = cases.value.findIndex(c => c.id === id)
      if (index !== -1) {
        cases.value[index] = updatedCase
      }
      if (currentCase.value && currentCase.value.id === id) {
        currentCase.value = updatedCase
      }
      
      return updatedCase
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const deleteCase = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/cases/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete test case')
      
      // Update local state
      cases.value = cases.value.filter(c => c.id !== id)
      if (currentCase.value && currentCase.value.id === id) {
        currentCase.value = null
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    cases,
    currentCase,
    loading,
    error,
    fetchCases,
    fetchCase,
    createCase,
    updateCase,
    deleteCase
  }
})
