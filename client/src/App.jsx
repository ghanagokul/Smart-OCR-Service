import React, { useEffect, useState } from 'react'
import UploadArea from './components/UploadArea'
import JobCard from './components/JobCard'
import SearchBar from './components/SearchBar'
import SearchResults from './components/SearchResults'
import { getStatus, searchDocs, getDownloadUrl } from './api'

export default function App() {
  const [jobs, setJobs] = useState(() => {
    const saved = localStorage.getItem('jobs')
    return saved ? JSON.parse(saved) : []
  })
  const [results, setResults] = useState([])

  useEffect(() => { localStorage.setItem('jobs', JSON.stringify(jobs)) }, [jobs])

  useEffect(() => {
    const interval = setInterval(async () => {
      const updated = await Promise.all(jobs.map(async j => {
        if (['COMPLETED','FAILED'].includes(j.status)) return j
        const s = await getStatus(j.id).catch(() => null)
        return s ? {...j, ...s} : j
      }))
      setJobs(updated)
    }, 1500)
    return () => clearInterval(interval)
  }, [jobs])

  const handleSearch = async (q) => {
    const items = await searchDocs(q)
    setResults(items)
  }

  const handleDownload = async (id) => {
    try {
      const url = await getDownloadUrl(id)
      window.location.href = url
    } catch {
      alert('Download not available yet.')
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Smart OCR & Tagging</h1>
        <p>Upload, extract, tag, search and download your documents.</p>
      </header>

      <UploadArea onNewJob={(job) => setJobs([job, ...jobs])} />

      <SearchBar onSearch={handleSearch} />
      <SearchResults items={results} onDownload={handleDownload} />

      <section className="jobs">
        {jobs.length === 0 && <p className="empty">No jobs yet. Upload a file to begin.</p>}
        {jobs.map(job => <JobCard key={job.id} job={job} />)}
      </section>
    </div>
  )
}