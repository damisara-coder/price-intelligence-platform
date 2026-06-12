import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function StatsPage() {
  const [stats, setStats] = useState([]);
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const platformColors = { jumia: '#FF5C00', marjane: '#2563EB', micromagma: '#10B981', zara: '#CE93D8' };

  // 🟢 Fonction pour récupérer les statistiques - VERSION DYNAMIQUE
  const fetchStats = async () => {
    setLoading(true);
    try {
      // ✅ UTILISATION DE L'ENDPOINT DYNAMIQUE
      const url = category 
        ? `http://localhost:8001/api/stats/dynamic?category_normalized=${category}` 
        : 'http://localhost:8001/api/stats/dynamic';
      
      const res = await fetch(url);
      const data = await res.json();
      
      // Filtrer les données pour n'afficher que les valeurs > 0
      const filteredData = (data.data || []).filter(item => item.mean > 0);
      setStats(filteredData);
      setLastUpdate(new Date());
      
      const uniqueCats = [...new Set((filteredData || []).map(s => s.category))];
      setCategories(uniqueCats);
    } catch (error) {
      console.error('Erreur:', error);
    }
    setLoading(false);
  };

  // 🟢 Auto-refresh toutes les 10 secondes (plus fréquent pour voir les changements)
  useEffect(() => {
    fetchStats();
    const interval = setInterval(() => {
      console.log('🔄 Mise à jour des statistiques dynamiques...');
      fetchStats();
    }, 10000); // Toutes les 10 secondes
    return () => clearInterval(interval);
  }, [category]);

  // Données pour le graphique (uniquement les valeurs > 0)
  const chartData = stats.reduce((acc, item) => {
    const existing = acc.find(i => i.category === item.category);
    if (existing) {
      if (item.mean > 0) existing[item.platform] = Math.round(item.mean);
    } else {
      const newEntry = { category: item.category };
      if (item.mean > 0) newEntry[item.platform] = Math.round(item.mean);
      acc.push(newEntry);
    }
    return acc;
  }, []);

  return (
    <div style={{ padding: 28, background: '#0a0c10', minHeight: '100vh' }}>
      
      {/* En-tête avec auto-refresh */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap' }}>
        <h2 style={{ color: '#fff', margin: 0 }}>Statistiques avancées</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <div style={{ color: '#4a5a7a', fontSize: 11, fontFamily: 'monospace' }}>
            📅 Dernière MAJ: {lastUpdate.toLocaleTimeString()}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#10B98122', padding: '4px 12px', borderRadius: 20 }}>
            <span style={{ width: 6, height: 6, background: '#10B981', borderRadius: '50%', animation: 'pulse 2s infinite' }}></span>
            <span style={{ color: '#10B981', fontSize: 10 }}>DYNAMIQUE (10s)</span>
          </div>
          <select value={category} onChange={(e) => setCategory(e.target.value)}
            style={{ background: '#162035', color: '#fff', border: '1px solid #2a3a50', padding: '10px 16px', borderRadius: 8 }}>
            <option value="">Toutes catégories</option>
            {categories.map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}
          </select>
        </div>
      </div>

      {/* Graphique comparatif */}
      <div style={{ background: '#162035', borderRadius: 16, padding: 20, marginBottom: 24 }}>
        <h3 style={{ color: '#fff', marginBottom: 20 }}>📊 Comparaison des prix moyens (MAD)</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3a50" />
            <XAxis dataKey="category" stroke="#8899bb" />
            <YAxis stroke="#8899bb" tickFormatter={(v) => `${v.toLocaleString()}`} />
            <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50', borderRadius: 8 }} 
                     formatter={(v, name) => [`${v?.toLocaleString() || 0} MAD`, name.charAt(0).toUpperCase() + name.slice(1)]} />
            <Legend />
            <Bar dataKey="jumia" fill={platformColors.jumia} radius={[4,4,0,0]} />
            <Bar dataKey="marjane" fill={platformColors.marjane} radius={[4,4,0,0]} />
            <Bar dataKey="micromagma" fill={platformColors.micromagma} radius={[4,4,0,0]} />
            <Bar dataKey="zara" fill={platformColors.zara} radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
        <div style={{ fontSize: 11, color: '#4a5a7a', textAlign: 'center', marginTop: 16 }}>
          💡 Les barres Zara apparaissent uniquement pour la catégorie "vetements"
        </div>
      </div>

      {/* Tableau des statistiques détaillées */}
      <div style={{ background: '#162035', borderRadius: 16, overflow: 'hidden', border: '1px solid #2a3a50' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #2a3a50', background: '#0d1420' }}>
          <span style={{ color: '#fff', fontWeight: 'bold' }}>📋 Données détaillées par plateforme</span>
          <span style={{ color: '#4a5a7a', fontSize: 11, marginLeft: 12 }}>{stats.length} lignes</span>
        </div>
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#8899bb' }}>Chargement des données...</div>
        ) : stats.length === 0 ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#4a5a7a' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
            <div>Aucune donnée pour cette catégorie</div>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2a3a50', background: '#0d1420' }}>
                <th style={{ padding: 12, textAlign: 'left', color: '#8899bb' }}>Catégorie</th>
                <th style={{ padding: 12, textAlign: 'left', color: '#8899bb' }}>Plateforme</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Moyenne (MAD)</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Médiane</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Min</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Max</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Écart-type</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Nb produits</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((item, idx) => (
                <tr key={idx} style={{ borderBottom: idx < stats.length - 1 ? '1px solid #2a3a50' : 'none' }}>
                  <td style={{ padding: 12, color: '#fff', fontWeight: 'bold', textTransform: 'capitalize' }}>
                    {item.category === 'vetements' ? '👕 Vêtements' : item.category === 'smartphones' ? '📱 Smartphones' : item.category === 'laptops' ? '💻 Laptops' : '📺 TV'}
                  </td>
                  <td style={{ padding: 12, color: platformColors[item.platform], fontWeight: 'bold', textTransform: 'capitalize' }}>
                    {item.platform === 'zara' ? '👗 Zara' : item.platform === 'jumia' ? '🛒 Jumia' : item.platform === 'marjane' ? '🏪 Marjane' : '⚡ Micromagma'}
                  </td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#10B981', fontFamily: 'monospace', fontWeight: 'bold' }}>
                    {Math.round(item.mean).toLocaleString()} MAD
                  </td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#fff', fontFamily: 'monospace' }}>
                    {Math.round(item.median).toLocaleString()} MAD
                  </td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#8899bb', fontFamily: 'monospace' }}>
                    {Math.round(item.min).toLocaleString()} MAD
                  </td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#8899bb', fontFamily: 'monospace' }}>
                    {Math.round(item.max).toLocaleString()} MAD
                  </td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#8899bb', fontFamily: 'monospace' }}>
                    {Math.round(item.std).toLocaleString()}
                  </td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#8899bb', fontFamily: 'monospace' }}>
                    {item.count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Légende */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: 24, 
        marginTop: 24, 
        padding: 12, 
        flexWrap: 'wrap',
        borderTop: '1px solid #2a3a50'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, background: '#FF5C00', borderRadius: 2 }}></div>
          <span style={{ fontSize: 11, color: '#8899bb' }}>Jumia</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, background: '#2563EB', borderRadius: 2 }}></div>
          <span style={{ fontSize: 11, color: '#8899bb' }}>Marjane</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, background: '#10B981', borderRadius: 2 }}></div>
          <span style={{ fontSize: 11, color: '#8899bb' }}>Micromagma</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, background: '#CE93D8', borderRadius: 2 }}></div>
          <span style={{ fontSize: 11, color: '#8899bb' }}>Zara (vêtements uniquement)</span>
        </div>
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