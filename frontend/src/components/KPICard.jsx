import React from 'react'

export default function KPICard({ value, label, color }) {
  return (
    <div style={{ background: '#162035', border: '1px solid #2a3a50', borderRadius: 16, padding: 20 }}>
      <div style={{ fontSize: 28, fontWeight: 800, color: color || '#fff' }}>{value ?? '—'}</div>
      <div style={{ fontSize: 12, color: '#8899bb' }}>{label}</div>
    </div>
  )
}