import axios from "axios";

/**
 * API base resolution:
 * 1. Vite env (preferred)
 * 2. Runtime-injected global (Docker / reverse proxy)
 * 3. Local development fallback
 */
export const API_BASE =
  import.meta.env.VITE_API_BASE?.trim() ||
  window.__API_BASE__ ||
  "http://localhost:8080";

/**
 * Centralized Axios client
 */
const api = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
});

/**
 * Safe execution wrapper.
 * Ensures API failures never crash the UI.
 */
async function safe(fn) {
  try {
    return await fn();
  } catch (err) {
    console.error("API Error:", err?.response || err);
    return null;
  }
}

/* ================================
   OCR / JOB APIs
   ================================ */

/**
 * Upload a document for OCR processing
 */
export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await safe(() =>
    api.post("/api/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  );

  return res?.data || null;
}

/**
 * Get job status (authoritative backend state)
 */
export async function getStatus(jobId) {
  const res = await safe(() =>
    api.get(`/api/status/${jobId}`)
  );
  return res?.data || null;
}

/**
 * Get OCR result payload
 */
export async function getResult(jobId) {
  const res = await safe(() =>
    api.get(`/api/result/${jobId}`)
  );
  return res?.data || null;
}

/**
 * Get download URL for processed document
 */
export async function getDownloadUrl(jobId) {
  const res = await safe(() =>
    api.get(`/api/download/${jobId}`)
  );
  return res?.data?.url || null;
}

/* ================================
   SEARCH
   ================================ */

/**
 * Search indexed documents
 */
export async function searchDocs(query) {
  const res = await safe(() =>
    api.get("/api/search", { params: { q: query } })
  );
  return res?.data?.results || [];
}

/* ================================
   CHAT / DOCUMENT QA
   ================================ */

/**
 * Ask a question about a processed document
 */
export async function askDocumentQuestion(docId, question) {
  const res = await safe(() =>
    api.post(`/api/chat/${docId}`, { question })
  );
  return res?.data || null;
}
