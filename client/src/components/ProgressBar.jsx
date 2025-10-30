import React from 'react'

export default function ProgressBar({ value = 0, label = '' }) {
  return (
    <div className="progress">
      <div className="bar" style={{ width: `${Math.min(100, Number(value) || 0)}%` }} />
      <span className="label">{label} {Math.round(value)}%</span>
    </div>
  )
}