import React, { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import LivePage from './pages/LivePage';
import AlertsPage from './pages/AlertsPage';
import StatsPage from './pages/StatsPage';

function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const pages = {
    dashboard: <DashboardPage />,
    live: <LivePage />,
    alerts: <AlertsPage />,
    stats: <StatsPage />
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'live', label: 'Live Prices' },
    { id: 'alerts', label: 'Alerts' },
    { id: 'stats', label: 'Statistics' }
  ];

  return (
    <div>
      {/* Sidebar */}
      <div style={{ width: 220, background: '#0d1420', borderRight: '1px solid #2a3a50', height: '100vh', position: 'fixed', left: 0, top: 0, zIndex: 100 }}>
        <div style={{ padding: '24px 20px', borderBottom: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 18, fontWeight: 'bold', color: '#fff' }}>PriceIntel</div>
          <div style={{ fontSize: 10, color: '#4a5a7a' }}>MAROC · MAD</div>
        </div>
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActivePage(item.id)}
            style={{
              display: 'block',
              width: '100%',
              padding: '12px 20px',
              background: activePage === item.id ? 'rgba(255,92,0,0.15)' : 'transparent',
              border: 'none',
              color: activePage === item.id ? '#FF5C00' : '#8899bb',
              cursor: 'pointer',
              textAlign: 'left',
              fontSize: 14,
              fontFamily: 'inherit'
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Topbar */}
      <div style={{ height: 56, background: '#0d1420', borderBottom: '1px solid #2a3a50', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', padding: '0 28px', marginLeft: 220 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', color: '#10B981', padding: '5px 12px', borderRadius: 20, fontSize: 11 }}>
          <span style={{ width: 6, height: 6, background: '#10B981', borderRadius: '50%', display: 'inline-block' }}></span>
          LIVE
        </div>
      </div>

      {/* Price Ticker */}
      <div style={{ background: '#0d1420', borderBottom: '1px solid #2a3a50', padding: '10px 28px', marginLeft: 220 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', color: '#10B981', padding: '5px 12px', borderRadius: 20, fontSize: 11 }}>
          <span style={{ width: 6, height: 6, background: '#10B981', borderRadius: '50%', display: 'inline-block' }}></span>
          📊 Real-time price monitoring active
        </div>
      </div>

      {/* Page Content */}
      <div style={{ marginLeft: 220, minHeight: '100vh', background: '#0a0c10' }}>
        {pages[activePage]}
      </div>
    </div>
  );
}

export default App;