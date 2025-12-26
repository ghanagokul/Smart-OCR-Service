export default function DocumentViewer({ fileUrl, onClose }) {
  if (!fileUrl) return null;

  // PDF.js viewer URL (backend-served PDF)
  const viewerSrc = `/pdfjs/web/viewer.html?file=${encodeURIComponent(
    fileUrl
  )}`;

  return (
    <div className="pdf-overlay" role="dialog" aria-modal="true">
      {/* Close button */}
      <button
        className="pdf-close"
        onClick={onClose}
        aria-label="Close document viewer"
      >
        ✕ Close
      </button>

      {/* PDF Viewer */}
      <iframe
        className="pdf-frame"
        title="PDF Viewer"
        src={viewerSrc}
      />
    </div>
  );
}
