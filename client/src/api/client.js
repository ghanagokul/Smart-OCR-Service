// src/api/client.js
import axios from "axios";

/**
 * API base resolution order:
 * 1. Vite environment variable (build-time)
 * 2. Runtime-injected global (Docker / reverse proxy)
 * 3. Local development fallback
 */
export const API_BASE =
  import.meta.env.VITE_API_BASE?.trim() ||
  window.__API_BASE__ ||
  "http://localhost:8080";

/**
 * Centralized Axios client for the monolithic backend.
 * All frontend API calls must go through this instance.
 */
export const api = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
  // withCredentials: true, // enable only if auth/cookies are added later
});

/**
 * Safe execution wrapper.
 * - Prevents UI crashes from failed API calls
 * - Standardizes error handling across the client
 *
 * @param {Function} fn - async API call
 * @returns {any|null} response or null on failure
 */
export async function safe(fn) {
  try {
    return await fn();
  } catch (err) {
    console.error("API Error:", err?.response || err);
    return null;
  }
}
