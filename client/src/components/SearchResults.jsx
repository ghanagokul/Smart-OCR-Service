import { JOB_STATUS } from "../constants/jobStatus";

export default function SearchResults({
  items,
  onDownload,
  onSelect,
  searching,
}) {
  if (searching) {
    return <p className="empty">Searching…</p>;
  }

  if (!items?.length) {
    return <p className="empty">No documents found.</p>;
  }

  return (
    <div className="results-grid" role="list">
      {items.map((item) => {
        const isCompleted = item.status === JOB_STATUS.COMPLETED;

        return (
          <div
            key={item.id}
            className="result-item"
            role="listitem"
          >
            {/* Metadata */}
            <div>
              <div className="result-title">{item.filename}</div>

              {item.tags?.length > 0 && (
                <div className="result-tags">
                  {item.tags.slice(0, 6).map((tag) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="result-actions">
              <button
                className="result-btn"
                onClick={() => onDownload?.(item.id)}
              >
                Download
              </button>

              <button
                className="result-btn"
                disabled={!isCompleted}
                onClick={() => onSelect?.(item)}
              >
                Chat
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
