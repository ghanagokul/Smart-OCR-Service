// src/api/ocr.api.js
import { api, safe } from "./client";

/**
 * Upload a document for OCR processing.
 *
 * Returns:
 * - { id, status, ... } on success
 * - null on failure
 */
export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await safe(() =>
    api.post("/api/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  );

  if (!res?.data) return null;

  const data = res.data;

  // ✅ NORMALIZE BACKEND RESPONSE
  return {
    id: data.id || data.document_id || data.job_id,
    status: data.status || "QUEUED",
    ...data,
  };
}


/**
 * Fetch the authoritative status of an OCR job.
 *
 * Returns:
 * - { id, status, progress?, error? } on success
 * - null on failure
 */
export async function getStatus(jobId) {
  const res = await safe(() =>
    api.get(`/api/status/${jobId}`)
  );
  return res?.data || null;
}

/**
 * Fetch OCR result payload for a completed job.
 *
 * Returns:
 * - result object on success
 * - null on failure
 */
export async function getResult(jobId) {
  const res = await safe(() =>
    api.get(`/api/result/${jobId}`)
  );
  return res?.data || null;
}

/**
 * Fetch a download URL for the processed document.
 *
 * Returns:
 * - string URL on success
 * - null on failure
 */
export async function getDownloadUrl(jobId) {
  const res = await safe(() =>
    api.get(`/api/download/${jobId}`)
  );
  return res?.data?.url || null;
}
