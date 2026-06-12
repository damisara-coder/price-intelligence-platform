import React from 'react'

export default function PriceTicker() {
  return (
    <div style={{ background: '#0d1420', borderBottom: '1px solid #222', padding: '10px 28px', marginLeft: 240 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', color: '#10B981', padding: '5px 12px', borderRadius: 20, fontSize: 11, width: 'fit-content' }}>
        <span style={{ width: 6, height: 6, background: '#10B981', borderRadius: '50%', animation: 'pulse 1.5s infinite' }}></span>
        📊 Real-time price monitoring active
      </div>
    </div>
  )
}