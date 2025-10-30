import React from 'react'

export default function SearchResults({ items, onDownload }) {
  if (!items || items.length === 0) {
    return <div className="card"><p className="empty">No results yet.</p></div>
  }
  return (
    <div className="card">
      <h3>Results</h3>
      {items.map(it => (
        <div key={it.id} className="row space" style={{ marginBottom: 10 }}>
          <div>
            <div style={{ fontWeight: 600 }}>{it.filename}</div>
            <div style={{ fontSize: 12, color: '#99a3ff' }}>
              {Array.isArray(it.tags) && it.tags.slice(0,6).map(t => (
                <span key={t} style={{ marginRight: 8, background:'#0a0f22', padding:'2px 8px', borderRadius: 10, border:'1px solid #26306b' }}>{t}</span>
              ))}
            </div>
          </div>
          <button onClick={() => onDownload(it.id)}>Download</button>
        </div>
      ))}
    </div>
  )
}