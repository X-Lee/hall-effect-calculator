<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="app-aside">
      <div class="logo-area">
        <el-icon :size="24"><VideoCamera /></el-icon>
        <span v-show="!isCollapsed" class="logo-text">B站切片工具</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapsed"
        router
        class="side-menu"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
        >
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <template #title>{{ route.meta.title }}</template>
        </el-menu-item>
      </el-menu>
      <div class="collapse-btn" @click="isCollapsed = !isCollapsed">
        <el-icon><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
      </div>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <h2>{{ currentTitle }}</h2>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { routes } from './router'

const route = useRoute()
const isCollapsed = ref(false)

const menuRoutes = computed(() =>
  routes.filter((r) => r.meta && r.meta.title)
)

const currentRoute = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '')
</script>

<style>
body {
  margin: 0;
  background: #f5f7fa;
}
.app-layout {
  height: 100vh;
}
.app-aside {
  background: #1d1e1f;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
}
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  border-bottom: 1px solid #333;
}
.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}
.side-menu {
  flex: 1;
  border-right: none;
  background: #1d1e1f;
}
.side-menu .el-menu-item {
  color: #bbb;
}
.side-menu .el-menu-item:hover,
.side-menu .el-menu-item.is-active {
  color: #fff;
  background: #409eff22;
}
.collapse-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  cursor: pointer;
  border-top: 1px solid #333;
}
.collapse-btn:hover {
  color: #fff;
}
.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 60px;
}
.app-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}
.app-main {
  padding: 20px;
  overflow-y: auto;
}
</style>
