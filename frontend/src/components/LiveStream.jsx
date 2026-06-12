import React from 'react';
import { useSSE } from '../hooks/useSSE';

export default function LiveStream() {
  const { data, connected } = useSSE('http://localhost:8001/api/stream/dashboard');

  if (!connected) {
    return (
      <div style={{ background: '#162035', borderRadius: 16, padding: 16, marginBottom: 24, border: '1px solid #FF5252' }}>
        <div style={{ color: '#FF5252', fontSize: 12 }}>🔌 Connexion au stream... en attente</div>
      </div>
    );
  }

  return (
    <div style={{ background: '#162035', borderRadius: 16, padding: 16, marginBottom: 24, border: '1px solid #10B981' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 11, color: '#8899bb' }}>📊 DONNÉES TEMPS RÉEL (SCRAPERS)</div>
          <div style={{ fontSize: 10, color: '#10B981', marginTop: 4 }}>
            {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'En attente...'}
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontSize: 10, color: '#8899bb' }}>📱 Smartphones</span>
            <div style={{ fontSize: 18, fontWeight: 'bold', color: '#00E5FF' }}>
              {data?.prices?.smartphones?.toLocaleString()} MAD
            </div>
            {data?.prices?.variation_smartphones !== 0 && (
              <div style={{ fontSize: 10, color: data?.prices?.variation_smartphones > 0 ? '#FF5252' : '#00E676' }}>
                {data?.prices?.variation_smartphones > 0 ? '↑' : '↓'} {Math.abs(data?.prices?.variation_smartphones)}%
              </div>
            )}
          </div>
          
          <div>
            <span style={{ fontSize: 10, color: '#8899bb' }}>💻 Laptops</span>
            <div style={{ fontSize: 18, fontWeight: 'bold', color: '#00E676' }}>
              {data?.prices?.laptops?.toLocaleString()} MAD
            </div>
            {data?.prices?.variation_laptops !== 0 && (
              <div style={{ fontSize: 10, color: data?.prices?.variation_laptops > 0 ? '#FF5252' : '#00E676' }}>
                {data?.prices?.variation_laptops > 0 ? '↑' : '↓'} {Math.abs(data?.prices?.variation_laptops)}%
              </div>
            )}
          </div>
          
          <div>
            <span style={{ fontSize: 10, color: '#8899bb' }}>📺 TV</span>
            <div style={{ fontSize: 18, fontWeight: 'bold', color: '#FFC107' }}>
              {data?.prices?.tv?.toLocaleString()} MAD
            </div>
          </div>
          
          <div>
            <span style={{ fontSize: 10, color: '#8899bb' }}>👕 Vêtements</span>
            <div style={{ fontSize: 18, fontWeight: 'bold', color: '#CE93D8' }}>
              {data?.prices?.vetements?.toLocaleString()} MAD
            </div>
          </div>
          
          <div>
            <span style={{ fontSize: 10, color: '#8899bb' }}>🔔 Alertes</span>
            <div style={{ fontSize: 18, fontWeight: 'bold', color: '#FF5252' }}>
              {data?.kpis?.active_alerts || 0}
            </div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, background: '#10B981', borderRadius: '50%', animation: 'pulse 2s infinite' }}></span>
          <span style={{ fontSize: 10, color: '#10B981' }}>SCRAPING LIVE</span>
        </div>
      </div>
      
      {/* Mini barre des prix par plateforme */}
      <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #2a3a50', display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <span style={{ fontSize: 10, color: '#8899bb' }}>Prix moyens par plateforme:</span>
        <span style={{ fontSize: 11, color: '#FF5C00' }}>Jumia: {data?.by_platform?.jumia?.toLocaleString()} MAD</span>
        <span style={{ fontSize: 11, color: '#2563EB' }}>Marjane: {data?.by_platform?.marjane?.toLocaleString()} MAD</span>
        <span style={{ fontSize: 11, color: '#10B981' }}>Micromagma: {data?.by_platform?.micromagma?.toLocaleString()} MAD</span>
        <span style={{ fontSize: 11, color: '#CE93D8' }}>Zara: {data?.by_platform?.zara?.toLocaleString()} MAD</span>
      </div>
      
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  );
}