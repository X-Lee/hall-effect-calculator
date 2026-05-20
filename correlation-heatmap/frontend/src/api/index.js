import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function generateHeatmap(params) {
  return api.post('/generate', params)
}

export function getColormaps() {
  return api.get('/colormaps')
}

export function getExportUrl(taskId, format = 'png', dpi = 300) {
  return `/api/export/${taskId}?format=${format}&dpi=${dpi}`
}

export function exportLagData(params) {
  return api.post('/export-lag-data', params, { responseType: 'blob' })
}
