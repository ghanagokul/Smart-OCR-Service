/**
 * Canonical OCR job lifecycle states.
 *
 * These values MUST exactly match backend responses.
 * Do not rename without backend coordination.
 */
export const JOB_STATUS = Object.freeze({
    UPLOADED: "UPLOADED",
    QUEUED: "QUEUED",
    PROCESSING: "PROCESSING",
    EXTRACTING: "EXTRACTING",
    INDEXING: "INDEXING",
    COMPLETED: "COMPLETED",
    FAILED: "FAILED",
  });
  
  /**
   * Terminal states — job will not transition further.
   */
  export const TERMINAL_JOB_STATUSES = Object.freeze([
    JOB_STATUS.COMPLETED,
    JOB_STATUS.FAILED,
  ]);
  
  /**
   * Active (non-terminal) states — job is still in progress.
   */
  export const ACTIVE_JOB_STATUSES = Object.freeze([
    JOB_STATUS.UPLOADED,
    JOB_STATUS.QUEUED,
    JOB_STATUS.PROCESSING,
    JOB_STATUS.EXTRACTING,
    JOB_STATUS.INDEXING,
  ]);
  