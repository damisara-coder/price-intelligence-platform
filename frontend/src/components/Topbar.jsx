import React, { useState, useEffect } from 'react'

export default function Topbar({ title, connected }) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTime = (date) => {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  return (
    <div style={{ height: 60, background: '#0d1420', borderBottom: '1px solid #222', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 28px', marginLeft: 240 }}>
      <div>
        <h1 style={{ fontSize: 18, color: '#fff', margin: 0 }}>{title}</h1>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', color: '#10B981', padding: '5px 12px', borderRadius: 20, fontSize: 11 }}>
          <span style={{ width: 6, height: 6, background: '#10B981', borderRadius: '50%', animation: 'pulse 1.5s infinite' }}></span>
          {connected ? ' LIVE' : ' OFFLINE'}
        </div>
        <div style={{ fontFamily: 'monospace', fontSize: 12, color: '#4a5a7a' }}>{formatTime(time)}</div>
      </div>
    </div>
  )
}