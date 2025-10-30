import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080'

export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await axios.post(`${API_BASE}/api/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data // { job_id }
}

export async function getStatus(jobId) {
  const { data } = await axios.get(`${API_BASE}/api/status/${jobId}`)
  return data
}

export async function getResult(jobId) {
  const { data } = await axios.get(`${API_BASE}/api/result/${jobId}`)
  return data
}

export async function searchDocs(q) {
    const { data } = await axios.get(`${API_BASE}/api/search`, { params: { q } })
    return data.results || []
}

export async function getDownloadUrl(jobId) {
    const { data } = await axios.get(`${API_BASE}/api/download/${jobId}`)
    return data.url
}