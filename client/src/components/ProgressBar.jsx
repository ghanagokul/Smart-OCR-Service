export default function ProgressBar({ value = 0, label = "" }) {
  const pct = Math.min(100, Math.max(0, Number(value) || 0));

  return (
    <div
      className="progress-bar"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={pct}
      aria-label={label || "Progress"}
    >
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${pct}%` }}
        />
      </div>

      <span className="progress-label">
        {label ? `${label} — ` : ""}
        {pct}%
      </span>
    </div>
  );
}
