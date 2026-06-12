import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [threshold, setThreshold] = useState(-10);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8001/api/generate-alerts');
      const data = await res.json();
      
      const filtered = data.alerts.filter(alert => alert.baisse >= Math.abs(threshold));
      setAlerts(filtered);
      setLastUpdate(new Date());
      
      const alertStats = filtered.reduce((acc, alert) => {
        if (alert.baisse >= 30) acc.critical++;
        else if (alert.baisse >= 20) acc.high++;
        else if (alert.baisse >= 15) acc.medium++;
        else acc.low++;
        return acc;
      }, { critical: 0, high: 0, medium: 0, low: 0 });
      
      setStats([
        { name: 'Critique (>30%)', value: alertStats.critical, color: '#FF5252' },
        { name: 'Élevée (>20%)', value: alertStats.high, color: '#FF8A65' },
        { name: 'Moyenne (>15%)', value: alertStats.medium, color: '#FFC107' },
        { name: 'Faible (>10%)', value: alertStats.low, color: '#00E676' }
      ]);
    } catch (error) {
      console.error('Erreur:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(() => {
      fetchAlerts();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [threshold]);

  const getSeverityColor = (baisse) => {
    if (baisse >= 30) return '#FF5252';
    if (baisse >= 20) return '#FF8A65';
    if (baisse >= 15) return '#FFC107';
    return '#00E676';
  };

  const getSeverityLabel = (baisse) => {
    if (baisse >= 30) return 'CRITIQUE';
    if (baisse >= 20) return 'ÉLEVÉE';
    if (baisse >= 15) return 'MOYENNE';
    return 'FAIBLE';
  };

  return (
    <div style={{ padding: 28, background: '#0a0c10', minHeight: '100vh' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap' }}>
        <h2 style={{ color: '#fff', margin: 0 }}>Alertes de prix</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ color: '#4a5a7a', fontSize: 11 }}>
            📅 Mise à jour: {lastUpdate.toLocaleTimeString()}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#10B98122', padding: '4px 12px', borderRadius: 20 }}>
            <span style={{ width: 6, height: 6, background: '#10B981', borderRadius: '50%', animation: 'pulse 2s infinite' }}></span>
            <span style={{ color: '#10B981', fontSize: 10 }}>LIVE</span>
          </div>
        </div>
      </div>

      {/* Filtre seuil */}
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        <label style={{ color: '#8899bb' }}>Seuil de baisse:</label>
        <select value={threshold} onChange={(e) => setThreshold(Number(e.target.value))}
          style={{ background: '#162035', color: '#fff', border: '1px solid #2a3a50', padding: '8px 16px', borderRadius: 8 }}>
          <option value={-5}>-5%</option>
          <option value={-10}>-10%</option>
          <option value={-15}>-15%</option>
          <option value={-20}>-20%</option>
          <option value={-30}>-30%</option>
        </select>
      </div>

      {/* Graphique distribution */}
      <div style={{ background: '#162035', borderRadius: 16, padding: 20, marginBottom: 24 }}>
        <h3 style={{ color: '#fff', marginBottom: 20 }}>Distribution des alertes par sévérité</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={stats}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3a50" />
            <XAxis dataKey="name" stroke="#8899bb" tick={{ fontSize: 11 }} />
            <YAxis stroke="#8899bb" />
            <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50' }} />
            <Bar dataKey="value" radius={[8,8,0,0]}>
              {stats.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Liste des alertes */}
      <div style={{ background: '#162035', borderRadius: 16, overflow: 'hidden', border: '1px solid #2a3a50' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #2a3a50', background: '#0d1420', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#fff', fontWeight: 'bold' }}>🔔 Alertes récentes</span>
          <span style={{ color: '#4a5a7a', fontSize: 11 }}>{alerts.length} alertes</span>
        </div>
        
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#8899bb' }}>Chargement...</div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#4a5a7a' }}>
            <div style={{ fontSize: 48 }}>✅</div>
            <div>Aucune alerte pour ce seuil</div>
          </div>
        ) : (
          <div style={{ padding: 16 }}>
            {alerts.map((alert, idx) => (
              <div key={idx} style={{ 
                background: '#0d1420', 
                borderRadius: 12, 
                padding: 16, 
                marginBottom: 12,
                borderLeft: `4px solid ${getSeverityColor(alert.baisse)}`
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <span style={{ 
                        background: getSeverityColor(alert.baisse), 
                        padding: '2px 8px', 
                        borderRadius: 4, 
                        fontSize: 10, 
                        fontWeight: 'bold',
                        color: '#000'
                      }}>
                        {getSeverityLabel(alert.baisse)}
                      </span>
                      <span style={{ fontSize: 11, color: '#FF5C00' }}>{alert.plateforme}</span>
                      <span style={{ fontSize: 11, color: '#4a5a7a' }}>•</span>
                      <span style={{ fontSize: 11, color: '#8899bb' }}>{alert.categorie}</span>
                    </div>
                    <div style={{ color: '#fff', fontWeight: 'bold', marginBottom: 6 }}>{alert.produit}</div>
                    <div style={{ color: '#8899bb', fontSize: 12 }}>
                      <span style={{ textDecoration: 'line-through', color: '#4a5a7a' }}>{alert.avant?.toLocaleString()} MAD</span>
                      {' → '}
                      <span style={{ color: '#10B981', fontWeight: 'bold' }}>{alert.apres?.toLocaleString()} MAD</span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 24, fontWeight: 'bold', color: getSeverityColor(alert.baisse) }}>-{alert.baisse}%</div>
                    <div style={{ color: '#00E676', fontSize: 11 }}>Éco: {alert.economie?.toLocaleString()} MAD</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
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