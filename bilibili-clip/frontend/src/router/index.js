import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/clip',
  },
  {
    path: '/clip',
    name: 'VideoClip',
    component: () => import('../views/ClipView.vue'),
    meta: { title: '精彩切片', icon: 'VideoCamera' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { title: '系统设置', icon: 'Setting' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
export { routes }
