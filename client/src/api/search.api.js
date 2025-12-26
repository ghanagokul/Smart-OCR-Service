// src/api/search.api.js
import { api, safe } from "./client";

/**
 * Search indexed documents.
 *
 * Returns:
 * - Array of search results on success
 * - null on failure
 */
export async function searchDocs(query) {
  const res = await safe(() =>
    api.get("/api/search", { params: { q: query } })
  );

  return res?.data?.results ?? null;
}
