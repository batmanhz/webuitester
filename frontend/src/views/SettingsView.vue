<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const saving = ref(false)

const form = ref({
  provider: 'lm studio',
  name: '',
  base_url: '',
  api_key: '',
  temperature: 0.0,
  thinking: false,
  headless: false
})

const fetchConfig = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:19000/api/config')
    if (!response.ok) throw new Error('Failed to fetch config')
    const data = await response.json()
    form.value = { ...form.value, ...data }
  } catch (e: any) {
    ElMessage.error(e.message || 'Failed to load settings')
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const response = await fetch('http://localhost:19000/api/config', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    if (!response.ok) throw new Error('Failed to save config')
    ElMessage.success('Settings saved successfully')
  } catch (e: any) {
    ElMessage.error(e.message || 'Failed to save settings')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<template>
  <div class="settings-view" v-loading="loading">
    <div class="header">
      <h1>Settings</h1>
      <el-button type="primary" @click="saveConfig" :loading="saving">Save Changes</el-button>
    </div>
    
    <div class="settings-content">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>LLM Configuration</span>
          </div>
        </template>
        
        <el-form :model="form" label-position="top">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Provider">
                <el-select v-model="form.provider" placeholder="Select provider" style="width: 100%">
                  <el-option label="LM Studio" value="lm studio" />
                  <el-option label="OpenAI" value="openai" />
                  <el-option label="Azure OpenAI" value="azure_openai" />
                  <el-option label="Anthropic" value="anthropic" />
                  <el-option label="Ollama" value="ollama" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Model Name">
                <el-input v-model="form.name" placeholder="e.g. gpt-4o or qwen2.5-7b" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Base URL">
            <el-input v-model="form.base_url" placeholder="http://localhost:1234/v1" />
          </el-form-item>
          
          <el-form-item label="API Key">
            <el-input v-model="form.api_key" type="password" show-password placeholder="Enter API Key" />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
               <el-form-item label="Temperature">
                <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
              </el-form-item>
            </el-col>
            <el-col :span="12">
               <el-form-item label="Features">
                 <div class="feature-toggles">
                   <el-checkbox v-model="form.thinking" label="Enable Thinking (Reasoning)" border />
                 </div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <el-card class="box-card" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <span>Browser Configuration</span>
          </div>
        </template>
        <el-form :model="form" label-position="top">
             <el-form-item label="Execution Mode">
                 <el-checkbox v-model="form.headless" label="Headless Mode (No Visible Browser)" border />
              </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  padding: 40px;
  max-width: 100%;
  margin: 0;
  height: 100%;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 1px solid var(--el-border-color-light);
  padding-bottom: 20px;
}

.settings-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 30px;
}

.feature-toggles {
  display: flex;
  gap: 15px;
}
</style>
