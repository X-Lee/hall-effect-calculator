import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export function submitVideo(url) {
  return api.post('/video/submit', { url })
}

export function getTaskInfo(taskId) {
  return api.get(`/video/${taskId}/info`)
}

export function startAnalysis(taskId, config = {}) {
  return api.post(`/analysis/${taskId}/start`, { task_id: taskId, ...config })
}

export function getAnalysisResults(taskId) {
  return api.get(`/analysis/${taskId}/results`)
}

export function rescoreAnalysis(taskId, weights, targetDuration) {
  return api.post(`/analysis/${taskId}/rescore`, {
    task_id: taskId,
    weights,
    target_duration: targetDuration,
  })
}

export function generateClip(taskId, segments, transition = 'crossfade', quality = 'balanced') {
  return api.post(`/export/${taskId}/generate`, {
    task_id: taskId,
    segments,
    transition,
    quality,
  })
}

export function getDownloadUrl(taskId) {
  return `/api/export/${taskId}/download`
}

export function getPreviewUrl(taskId) {
  return `/api/export/${taskId}/preview`
}

export function getSettings() {
  return api.get('/settings')
}

export function updateSettings(config) {
  return api.post('/settings', config)
}

export function createSSE(url) {
  return new EventSource(url)
}
