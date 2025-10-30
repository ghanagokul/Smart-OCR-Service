import React, { useState } from 'react'
import ProgressBar from './ProgressBar'
import { getResult } from '../api'

const pretty = (s) => {
  try { return JSON.stringify(JSON.parse(s), null, 2) } catch { return s }
}

export default function JobCard({ job }) {
  const [open, setOpen] = useState(false)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')

  const fetchResult = async () => {
    setErr('')
    try {
      const r = await getResult(job.id)
      setResult(r)
      setOpen(true)
    } catch (e) {
      setErr(e?.response?.data?.error || 'Not ready')
    }
  }

  return (
    <div className="card">
      <div className="row space">
        <div>
          <h3>{job.filename || 'Document'}</h3>
          <p className={`status ${job.status?.toLowerCase()}`}>{job.status} — {job.stage}</p>
        </div>
        <button onClick={fetchResult} disabled={job.status !== 'COMPLETED'}>
          {job.status === 'COMPLETED' ? 'View Result' : 'Processing…'}
        </button>
      </div>
      <ProgressBar value={job.progress || 0} label={job.stage || ''} />
      {err && <p className="error">{err}</p>}
      {open && result && (
        <div className="result">
          <h4>Extracted Text</h4>
          <pre className="code">{result.text}</pre>
          <h4>Entities (NER)</h4>
          <pre className="code">{pretty(result.entities)}</pre>
        </div>
      )}
    </div>
  )
}