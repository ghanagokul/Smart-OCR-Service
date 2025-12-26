import { useEffect, useRef, useState } from "react";
import { getStatus } from "../api/ocr.api";
import { TERMINAL_JOB_STATUSES } from "../constants/jobStatus";

export function useJobs(pollInterval = 2000) {
  const [jobs, setJobs] = useState([]);
  const pollRef = useRef(null);

  useEffect(() => {
    // Check if any job is still active
    const hasActiveJobs = jobs.some(
      (job) => !TERMINAL_JOB_STATUSES.includes(job.status)
    );

    // Start polling only if needed
    if (hasActiveJobs && !pollRef.current) {
      pollRef.current = setInterval(async () => {
        setJobs((prevJobs) =>
          Promise.all(
            prevJobs.map(async (job) => {
              if (TERMINAL_JOB_STATUSES.includes(job.status)) {
                return job;
              }

              const status = await getStatus(job.id);

              // Only update if status actually changed
              if (!status || status.status === job.status) {
                return job;
              }

              return { ...job, ...status };
            })
          )
        );
      }, pollInterval);
    }

    // Stop polling when no active jobs
    if (!hasActiveJobs && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [jobs, pollInterval]);

  function addJob(job) {
    setJobs((prev) => [job, ...prev]);
  }

  function clearJobs() {
    setJobs([]);
  }

  return { jobs, addJob, clearJobs };
}
