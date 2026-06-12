import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useSSE } from '../hooks/useSSE';

export default function LivePage() {
  const [prices, setPrices] = useState([]);
  const [platform, setPlatform] = useState('jumia');
  const [category, setCategory] = useState('smartphones');
  const [loading, setLoading] = useState(true);
  const [priceHistory, setPriceHistory] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // 🟢 Streaming temps réel pour les prix
  const { data: streamData, connected } = useSSE('http://localhost:8001/api/stream/dashboard');

  const platformColors = { jumia: '#FF5C00', marjane: '#2563EB', micromagma: '#10B981', zara: '#8B5CF6' };
  const categories = ['smartphones', 'laptops', 'tv', 'vetements'];

  // Fetch des prix initiaux
  const fetchPrices = async () => {
    try {
      const res = await fetch(`http://localhost:8001/api/prices?platform=${platform}&category=${category}&limit=50`);
      const data = await res.json();
      setPrices(data.data || []);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Erreur:', error);
    }
    setLoading(false);
  };

  // 🟢 Mettre à jour l'historique des prix avec les données du stream
  useEffect(() => {
    if (streamData && streamData.prices) {
      const currentPrice = category === 'smartphones' 
        ? streamData.prices.smartphones 
        : category === 'laptops'
        ? streamData.prices.laptops
        : category === 'tv'
        ? streamData.prices.tv
        : streamData.prices.vetements;

      if (currentPrice) {
        setPriceHistory(prev => {
          const newHistory = [...prev, {
            time: new Date().toLocaleTimeString(),
            price: currentPrice,
            timestamp: new Date()
          }];
          // Garder seulement les 20 derniers points
          return newHistory.slice(-20);
        });
      }
    }
  }, [streamData, category]);

  useEffect(() => {
    fetchPrices();
  }, [platform, category]);

  // Calcul de la variation en temps réel
  const getVariation = () => {
    if (priceHistory.length < 2) return { value: 0, isUp: true };
    const last = priceHistory[priceHistory.length - 1]?.price || 0;
    const prev = priceHistory[priceHistory.length - 2]?.price || last;
    const variation = last - prev;
    const percent = prev !== 0 ? (variation / prev) * 100 : 0;
    return { value: Math.abs(percent).toFixed(1), isUp: variation >= 0 };
  };

  const variation = getVariation();
  const currentPrice = category === 'smartphones' 
    ? streamData?.prices?.smartphones 
    : category === 'laptops'
    ? streamData?.prices?.laptops
    : category === 'tv'
    ? streamData?.prices?.tv
    : streamData?.prices?.vetements;

  return (
    <div style={{ padding: 28, background: '#0a0c10', minHeight: '100vh' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ color: '#fff', margin: 0 }}>Live Prices</h2>
        <div style={{ color: '#4a5a7a', fontSize: 12 }}>
          📅 Dernière mise à jour: {lastUpdate.toLocaleTimeString()}
        </div>
      </div>

      {/* Filtres */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
        <select value={platform} onChange={(e) => setPlatform(e.target.value)} 
          style={{ background: '#162035', color: '#fff', border: '1px solid #2a3a50', padding: '10px 16px', borderRadius: 8, cursor: 'pointer' }}>
          <option value="jumia">Jumia</option>
          <option value="marjane">Marjane</option>
          <option value="micromagma">Micromagma</option>
          <option value="zara">Zara</option>
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)} 
          style={{ background: '#162035', color: '#fff', border: '1px solid #2a3a50', padding: '10px 16px', borderRadius: 8, cursor: 'pointer' }}>
          {categories.map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}
        </select>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: connected ? '#10B98122' : '#FF525222', padding: '8px 16px', borderRadius: 20 }}>
          <span style={{ width: 8, height: 8, background: connected ? '#10B981' : '#FF5252', borderRadius: '50%', display: 'inline-block', animation: 'pulse 2s infinite' }}></span>
          <span style={{ color: connected ? '#10B981' : '#FF5252', fontSize: 12 }}>{connected ? 'STREAMING EN DIRECT' : 'CONNEXION PERDUE'}</span>
        </div>
      </div>

      {/* 🟢 CARTE PRIX ACTUEL EN TEMPS RÉEL */}
      <div style={{ 
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', 
        borderRadius: 16, 
        padding: 24, 
        marginBottom: 24,
        border: `2px solid ${platformColors[platform]}`,
        textAlign: 'center'
      }}>
        <div style={{ fontSize: 14, color: '#8899bb', marginBottom: 8 }}>PRIX ACTUEL EN TEMPS RÉEL</div>
        <div style={{ fontSize: 48, fontWeight: 'bold', color: platformColors[platform] }}>
          {currentPrice ? `${currentPrice.toLocaleString()} MAD` : 'Chargement...'}
        </div>
        {variation.value !== 0 && (
          <div style={{ 
            fontSize: 16, 
            color: variation.isUp ? '#FF5252' : '#00E676',
            marginTop: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8
          }}>
            {variation.isUp ? '↑' : '↓'} {variation.value}% depuis la dernière mise à jour
          </div>
        )}
        <div style={{ fontSize: 11, color: '#4a5a7a', marginTop: 12 }}>
          Mise à jour en temps réel toutes les 5 secondes via streaming SSE
        </div>
      </div>

      {/* 📈 Graphique d'évolution temps réel */}
      <div style={{ background: '#162035', borderRadius: 16, padding: 20, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ color: '#fff', margin: 0 }}>📈 Évolution des prix en temps réel</h3>
          <div style={{ fontSize: 11, color: '#4a5a7a' }}>
            📊 {priceHistory.length} points de données collectés
          </div>
        </div>
        
        {/* EXPLICATION DU GRAPHIQUE */}
        <div style={{ 
          background: '#0d1420', 
          borderRadius: 8, 
          padding: 12, 
          marginBottom: 16,
          borderLeft: `3px solid ${platformColors[platform]}`
        }}>
          <div style={{ fontSize: 11, color: '#8899bb' }}>
            💡 <strong>Comment lire ce graphique ?</strong> Cette courbe montre l'évolution du prix moyen des {category} 
            sur la plateforme <strong style={{ color: platformColors[platform] }}>{platform.toUpperCase()}</strong> en temps réel.
            Chaque point représente le prix à un instant T. Les variations sont simulées avec une marge de ±2% 
            pour visualiser les fluctuations du marché.
          </div>
        </div>

        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={priceHistory}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={platformColors[platform]} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={platformColors[platform]} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3a50" />
            <XAxis 
              dataKey="time" 
              stroke="#8899bb" 
              tick={{ fontSize: 10 }}
              label={{ value: 'Temps (secondes)', position: 'bottom', fill: '#8899bb', fontSize: 10 }}
            />
            <YAxis 
              stroke="#8899bb" 
              tick={{ fontSize: 10 }} 
              tickFormatter={(v) => `${v.toLocaleString()} MAD`}
              label={{ value: 'Prix (MAD)', angle: -90, position: 'insideLeft', fill: '#8899bb', fontSize: 10 }}
              domain={['auto', 'auto']}
            />
            <Tooltip 
              contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50', borderRadius: 8 }} 
              formatter={(v) => [`${v.toLocaleString()} MAD`, 'Prix']}
              labelFormatter={(label) => `Heure: ${label}`}
            />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke={platformColors[platform]} 
              strokeWidth={3}
              fill="url(#colorPrice)"
              dot={{ r: 4, fill: platformColors[platform], strokeWidth: 0 }}
              activeDot={{ r: 6 }}
            />
          </AreaChart>
        </ResponsiveContainer>
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: 24, 
          marginTop: 16,
          fontSize: 11,
          color: '#4a5a7a'
        }}>
          <div>📈 <span style={{ color: platformColors[platform] }}>Courbe des prix</span> - Tendance en temps réel</div>
          <div>🟢 <span style={{ color: '#00E676' }}>Hausse</span> / 🔴 <span style={{ color: '#FF5252' }}>Baisse</span></div>
          <div>⏱️ Mise à jour: toutes les 5 secondes</div>
        </div>
      </div>

      {/* Tableau des prix */}
      <div style={{ background: '#162035', borderRadius: 16, overflow: 'hidden', border: '1px solid #2a3a50' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #2a3a50', background: '#0d1420' }}>
          <span style={{ color: '#fff', fontWeight: 'bold' }}>📋 Catalogue des produits</span>
          <span style={{ color: '#4a5a7a', fontSize: 11, marginLeft: 12 }}>Liste des produits scrappés - mise à jour périodique</span>
        </div>
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#8899bb' }}>Chargement...</div>
        ) : prices.length === 0 ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#4a5a7a' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
            <div>Aucun produit trouvé pour {platform} / {category}</div>
            <div style={{ fontSize: 11, marginTop: 8 }}>Vérifiez que les données scrappées sont disponibles</div>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2a3a50', background: '#0d1420' }}>
                <th style={{ padding: 12, textAlign: 'left', color: '#8899bb' }}>Produit</th>
                <th style={{ padding: 12, textAlign: 'right', color: '#8899bb' }}>Prix (MAD)</th>
                <th style={{ padding: 12, textAlign: 'center', color: '#8899bb' }}>Catégorie</th>
                <th style={{ padding: 12, textAlign: 'center', color: '#8899bb' }}>Plateforme</th>
              </tr>
            </thead>
            <tbody>
              {prices.slice(0, 15).map((item, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #2a3a50' }}>
                  <td style={{ padding: 12, color: '#fff' }}>{item.name?.substring(0, 50)}</td>
                  <td style={{ padding: 12, textAlign: 'right', color: '#10B981', fontFamily: 'monospace', fontWeight: 'bold' }}>
                    {item.price?.toLocaleString()} MAD
                  </td>
                  <td style={{ padding: 12, textAlign: 'center', color: '#8899bb' }}>{item.category}</td>
                  <td style={{ padding: 12, textAlign: 'center' }}>
                    <span style={{ color: platformColors[item.source], fontWeight: 'bold' }}>{item.source}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      <div style={{ textAlign: 'center', marginTop: 24, padding: 12, borderTop: '1px solid #2a3a50' }}>
        <div style={{ fontSize: 10, color: '#4a5a7a' }}>
          🔄 Les données du graphique sont mises à jour en temps réel via SSE (Server-Sent Events)
          <br />📡 Les variations sont basées sur les données réelles des scrapers avec une marge de ±2% pour simuler les fluctuations du marché
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