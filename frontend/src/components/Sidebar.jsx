import React from 'react'
import { LayoutDashboard, TrendingUp, Bell, BarChart3 } from 'lucide-react'

export default function Sidebar({ activePage, onNavigate }) {
  const items = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'live', label: 'Live Prices', icon: TrendingUp },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'stats', label: 'Statistics', icon: BarChart3 },
  ]

  return (
    <div style={{ width: 240, background: '#0d1420', borderRight: '1px solid #222', height: '100vh', position: 'fixed', left: 0, top: 0 }}>
      <div style={{ padding: 24, borderBottom: '1px solid #222' }}>
        <div style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>PriceIntel</div>
        <div style={{ fontSize: 10, color: '#4a5a7a' }}>MAROC · MAD</div>
      </div>
      <nav style={{ padding: 16 }}>
        {items.map(item => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              width: '100%',
              padding: '10px 12px',
              background: activePage === item.id ? 'rgba(255,92,0,0.15)' : 'transparent',
              border: 'none',
              borderRadius: 8,
              color: activePage === item.id ? '#FF5C00' : '#8899bb',
              cursor: 'pointer',
              fontFamily: 'inherit',
              marginBottom: 4
            }}
          >
            <item.icon size={16} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}