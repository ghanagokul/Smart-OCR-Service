import { api, safe } from "./client";

/**
 * Ask a question about a processed document.
 *
 * Contract:
 * - Returns `{ answer: string, ... }` on success
 * - Returns `null` on failure
 * - Backend must accept only COMPLETED documents
 */
export async function askDocumentQuestion(docId, question) {
  const res = await safe(() =>
    api.post(`/api/chat/${docId}`, { question })
  );
  return res?.data || null;
}
