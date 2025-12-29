<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const activeIndex = ref('/')

const handleSelect = (key: string) => {
  router.push(key)
}
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="64px" class="sidebar">
        <el-menu
          :default-active="activeIndex"
          class="el-menu-vertical-demo"
          collapse
          background-color="#1e1e1e"
          text-color="#fff"
          active-text-color="#8B5CF6"
          @select="handleSelect"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>Home</template>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <template #title>Settings</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-main class="main-content">
          <RouterView />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.common-layout {
  height: 100vh;
  background-color: #121212;
  color: #fff;
}

.el-container {
  height: 100%;
}

.sidebar {
  border-right: 1px solid #333;
}

.el-menu {
  border-right: none;
}

.main-content {
  padding: 0;
  height: 100%;
}
</style>
