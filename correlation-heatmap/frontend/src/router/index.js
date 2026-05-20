import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/heatmap',
  },
  {
    path: '/heatmap',
    name: 'CorrelationHeatmap',
    component: () => import('../views/HeatmapView.vue'),
    meta: { title: '相关性热图', icon: 'DataAnalysis' },
  },
  {
    path: '/clip',
    name: 'BilibiliClip',
    meta: { title: 'B站切片', icon: 'VideoCamera', externalLink: 'http://localhost:5174' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
export { routes }
