import React, { useState } from 'react'

export default function SearchBar({ onSearch }) {
  const [q, setQ] = useState('')
  return (
    <div className="card">
      <div className="row">
        <input
          type="text"
          placeholder="Search by keywords, tags, text…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ flex: 1, padding: 10, borderRadius: 12, border: '1px solid #26306b', background:'#0e142b', color:'#c9d0ff' }}
        />
        <button onClick={() => onSearch(q)}>Search</button>
      </div>
    </div>
  )
}