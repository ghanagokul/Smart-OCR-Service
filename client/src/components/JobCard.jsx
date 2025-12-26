import ProgressBar from "./ProgressBar";
import { JOB_STATUS } from "../constants/jobStatus";

export default function JobCard({ job, onView }) {
  const isCompleted = job.status === JOB_STATUS.COMPLETED;
  const isFailed = job.status === JOB_STATUS.FAILED;

  return (
    <div className="job-card">
      <div className="row space-between">
        <div>
          <h4>{job.filename}</h4>
          <p className={`job-status ${job.status}`}>
            {job.status}
          </p>
        </div>

        <button
          className="result-btn"
          disabled={!isCompleted}
          onClick={() => onView?.(job)}
        >
          {isCompleted ? "View Document" : isFailed ? "Failed" : "Processing…"}
        </button>
      </div>

      {/* Progress only while job is active */}
      {!isCompleted && !isFailed && (
        <ProgressBar
          value={job.progress ?? 0}
          label={job.stage || "Processing"}
        />
      )}
    </div>
  );
}
