import React, { useRef, useState } from 'react'
import { uploadFile, getStatus } from '../api'

export default function UploadArea({ onNewJob }) {
  const inputRef = useRef()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    setBusy(true)
    try {
      const { job_id } = await uploadFile(file)
      const s = await getStatus(job_id)
      onNewJob({ id: job_id, filename: file.name, ...s })
    } catch (err) {
      setError(err?.response?.data?.error || 'Upload failed')
    } finally {
      setBusy(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div className="card">
      <div className="row">
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff"
          onChange={handleUpload}
          disabled={busy}
        />
        <button onClick={() => inputRef.current?.click()} disabled={busy}>
          Choose File
        </button>
      </div>
      {busy && <p>Uploading…</p>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}