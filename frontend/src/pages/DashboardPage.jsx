import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  ScatterChart, Scatter, ComposedChart, RadialBarChart, RadialBar,
  PieChart, Pie, Cell
} from 'recharts';
import { format } from 'date-fns';
import LiveStream from '../components/LiveStream';
import { useSSE } from '../hooks/useSSE';

export default function DashboardPage() {
  const [kpis, setKpis] = useState(null);
  const [stats, setStats] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // 🟢 STREAMING TEMPS RÉEL - Données qui changent en direct
  const { data: streamData, connected: streamConnected } = useSSE('http://localhost:8001/api/stream/dashboard');

  // Couleurs professionnelles
  const colors = {
    jumia: '#FF5C00',
    marjane: '#2563EB',
    micromagma: '#10B981',
    zara: '#8B5CF6',
    gradient: ['#00E5FF', '#00E676', '#FFC107', '#FF5252', '#CE93D8', '#4C9EFF']
  };

  // Fetch initial des données (une seule fois)
  const fetchInitialData = async () => {
    try {
      const [statsRes, alertsRes, pricesRes] = await Promise.all([
        fetch('http://localhost:8001/api/stats'),
        fetch('http://localhost:8001/api/alerts'),
        fetch('http://localhost:8001/api/prices?limit=100')
      ]);
      
      const statsData = await statsRes.json();
      setStats(statsData.data || []);
      const alertsData = await alertsRes.json();
      setAlerts(alertsData.alerts || []);
      const pricesData = await pricesRes.json();
      setPrices(pricesData.data || []);
      
    } catch (error) {
      console.error('Erreur:', error);
    }
    setLoading(false);
  };

  // 🟢 Mettre à jour les KPIs avec les données du stream
  useEffect(() => {
    if (streamData && streamData.kpis) {
      setKpis(streamData.kpis);
      setLastUpdate(new Date());
    }
  }, [streamData]);

  // Chargement initial
  useEffect(() => {
    fetchInitialData();
  }, []);

  // Filtrer les données
  const filteredStats = stats.filter(s => 
    (selectedPlatform === 'all' || s.platform === selectedPlatform) &&
    (selectedCategory === 'all' || s.category === selectedCategory)
  );

  // Données pour le graphique à barres (prix moyen par catégorie)
  const barData = stats.reduce((acc, item) => {
    const existing = acc.find(i => i.category === item.category);
    if (existing) {
      existing[item.platform] = Math.round(item.mean);
    } else {
      acc.push({ category: item.category, [item.platform]: Math.round(item.mean) });
    }
    return acc;
  }, []);

  // Données pour le graphique en lignes - Mise à jour avec les données du stream
  const lineData = [
    { name: 'Smartphones', price: kpis?.avg_smartphones_mad || 0 },
    { name: 'Laptops', price: kpis?.avg_laptops_mad || 0 },
    { name: 'TV', price: streamData?.prices?.tv || 0 },
    { name: 'Vêtements', price: streamData?.prices?.vetements || 0 },
  ];

  // Données pour le pie chart (répartition par plateforme)
  const platformDistribution = stats.reduce((acc, item) => {
    const existing = acc.find(p => p.name === item.platform);
    if (existing) {
      existing.value += item.count || 1;
    } else {
      acc.push({ name: item.platform, value: item.count || 1, color: colors[item.platform] });
    }
    return acc;
  }, []);

  // Données pour le scatter (prix vs catégorie) - Mise à jour dynamique
  const scatterData = [
    { category: 'Smartphones', price: kpis?.avg_smartphones_mad || 0, platform: 'global' },
    { category: 'Laptops', price: kpis?.avg_laptops_mad || 0, platform: 'global' },
    { category: 'TV', price: streamData?.prices?.tv || 0, platform: 'global' },
    { category: 'Vêtements', price: streamData?.prices?.vetements || 0, platform: 'global' },
  ];

  // Données pour le radial (distribution des prix par catégorie)
  const radialData = [
    { name: 'Smartphones', value: kpis?.avg_smartphones_mad || 0, fill: '#00E5FF' },
    { name: 'Laptops', value: kpis?.avg_laptops_mad || 0, fill: '#00E676' },
    { name: 'TV', value: streamData?.prices?.tv || 0, fill: '#FFC107' },
    { name: 'Vêtements', value: streamData?.prices?.vetements || 0, fill: '#CE93D8' },
  ];

  // Données pour les mini KPIs par plateforme
  const platformKPIs = ['jumia', 'marjane', 'micromagma', 'zara'].map(plat => ({
    platform: plat,
    avgPrice: streamData?.by_platform?.[plat] || 0,
    color: colors[plat]
  }));

  // Top produits les plus chers
  const topProducts = [...prices].sort((a, b) => b.price - a.price).slice(0, 5);

  // Alertes récentes
  const recentAlerts = alerts.slice(0, 4);

  // Statistiques générales
  const avgPriceOverall = stats.reduce((sum, s) => sum + s.mean, 0) / (stats.length || 1);
  const maxPrice = Math.max(...stats.map(s => s.max || 0), 0);
  const minPrice = Math.min(...stats.map(s => s.min || 999999), 999999);

  // 🟢 Variation en temps réel
  const variationSmartphones = streamData?.prices?.variation_smartphones || 0;
  const variationLaptops = streamData?.prices?.variation_laptops || 0;

  if (loading) return <div style={{ padding: 28, color: '#fff' }}>Chargement du dashboard...</div>;

  return (
    <div style={{ padding: 24, background: '#0a0c10', minHeight: '100vh' }}>
      
      {/* En-tête avec timestamp */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap' }}>
        <h2 style={{ color: '#fff', margin: 0 }}>Dashboard Intelligence</h2>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <select value={selectedPlatform} onChange={(e) => setSelectedPlatform(e.target.value)} style={{ background: '#162035', color: '#fff', border: '1px solid #2a3a50', padding: '6px 12px', borderRadius: 8 }}>
            <option value="all">Toutes plateformes</option>
            <option value="jumia">Jumia</option>
            <option value="marjane">Marjane</option>
            <option value="micromagma">Micromagma</option>
            <option value="zara">Zara</option>
          </select>
          <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} style={{ background: '#162035', color: '#fff', border: '1px solid #2a3a50', padding: '6px 12px', borderRadius: 8 }}>
            <option value="all">Toutes catégories</option>
            <option value="smartphones">Smartphones</option>
            <option value="laptops">Laptops</option>
            <option value="tv">TV</option>
            <option value="vetements">Vêtements</option>
          </select>
          <div style={{ color: '#4a5a7a', fontSize: 11, fontFamily: 'monospace' }}>
            📅 {format(lastUpdate, 'HH:mm:ss')}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: streamConnected ? '#10B98122' : '#FF525222', padding: '4px 12px', borderRadius: 20 }}>
            <span style={{ width: 6, height: 6, background: streamConnected ? '#10B981' : '#FF5252', borderRadius: '50%', animation: 'pulse 2s infinite' }}></span>
            <span style={{ color: streamConnected ? '#10B981' : '#FF5252', fontSize: 10 }}>{streamConnected ? 'LIVE' : 'OFFLINE'}</span>
          </div>
        </div>
      </div>

      {/* 🟢 BANDEAU STREAMING */}
      <LiveStream />

      {/* LIGNE 1: GRANDS KPIs - MIS À JOUR EN TEMPS RÉEL */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <div style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', borderRadius: 16, padding: 16, border: '1px solid rgba(0,229,255,0.2)' }}>
          <div style={{ fontSize: 11, color: '#00E5FF', marginBottom: 4 }}>📦 TOTAL PRODUITS</div>
          <div style={{ fontSize: 28, fontWeight: 'bold', color: '#fff' }}>{kpis?.total_products?.toLocaleString()}</div>
          <div style={{ fontSize: 10, color: '#4a5a7a', marginTop: 4 }}>sur 4 plateformes</div>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', borderRadius: 16, padding: 16, border: '1px solid rgba(0,230,118,0.2)' }}>
          <div style={{ fontSize: 11, color: '#00E676', marginBottom: 4 }}>🔔 ALERTES ACTIVES</div>
          <div style={{ fontSize: 28, fontWeight: 'bold', color: '#fff' }}>{kpis?.active_alerts}</div>
          <div style={{ fontSize: 10, color: '#4a5a7a', marginTop: 4 }}>baisses &gt;10%</div>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', borderRadius: 16, padding: 16, border: '1px solid rgba(255,193,7,0.2)' }}>
          <div style={{ fontSize: 11, color: '#FFC107', marginBottom: 4 }}>💰 SMARTPHONES</div>
          <div style={{ fontSize: 28, fontWeight: 'bold', color: '#fff' }}>{kpis?.avg_smartphones_mad?.toLocaleString()} MAD</div>
          <div style={{ fontSize: 10, color: variationSmartphones > 0 ? '#FF5252' : '#00E676', marginTop: 4 }}>
            {variationSmartphones > 0 ? '↑' : '↓'} {Math.abs(variationSmartphones)}% en temps réel
          </div>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', borderRadius: 16, padding: 16, border: '1px solid rgba(255,82,82,0.2)' }}>
          <div style={{ fontSize: 11, color: '#FF5252', marginBottom: 4 }}>💻 LAPTOPS</div>
          <div style={{ fontSize: 28, fontWeight: 'bold', color: '#fff' }}>{kpis?.avg_laptops_mad?.toLocaleString()} MAD</div>
          <div style={{ fontSize: 10, color: variationLaptops > 0 ? '#FF5252' : '#00E676', marginTop: 4 }}>
            {variationLaptops > 0 ? '↑' : '↓'} {Math.abs(variationLaptops)}% en temps réel
          </div>
        </div>
      </div>

      {/* LIGNE 2: Mini KPIs par plateforme + Top produits */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>🏷️ PRIX MOYEN PAR PLATEFORME (temps réel)</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            {platformKPIs.map(p => (
              <div key={p.platform} style={{ textAlign: 'center' }}>
                <div style={{ width: 40, height: 40, borderRadius: 20, background: `${p.color}22`, margin: '0 auto 8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ color: p.color, fontSize: 18 }}>📱</span>
                </div>
                <div style={{ fontSize: 11, color: p.color, fontWeight: 'bold', textTransform: 'uppercase' }}>{p.platform}</div>
                <div style={{ fontSize: 16, fontWeight: 'bold', color: '#fff' }}>{p.avgPrice?.toLocaleString() || '—'}</div>
                <div style={{ fontSize: 9, color: '#4a5a7a' }}>MAD</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>🔥 TOP 5 PRODUITS LES PLUS CHERS</div>
          {topProducts.map((p, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: i < 4 ? '1px solid #2a3a50' : 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ color: i === 0 ? '#FFC107' : '#8899bb', fontSize: 12 }}>{i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i+1}°`}</span>
                <span style={{ fontSize: 11, color: '#fff' }}>{p.name?.substring(0, 25)}...</span>
              </div>
              <span style={{ fontSize: 12, color: '#10B981', fontFamily: 'monospace' }}>{p.price?.toLocaleString()} MAD</span>
            </div>
          ))}
        </div>
      </div>

      {/* LIGNE 3: Graphique à barres (prix par catégorie) + Pie chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>📊 PRIX MOYEN PAR CATÉGORIE</div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a3a50" />
              <XAxis dataKey="category" stroke="#8899bb" tick={{ fontSize: 10 }} />
              <YAxis stroke="#8899bb" tick={{ fontSize: 10 }} tickFormatter={(v) => `${Math.round(v/1000)}k`} />
              <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50', fontSize: 11 }} formatter={(v) => [`${v.toLocaleString()} MAD`]} />
              <Bar dataKey="jumia" fill={colors.jumia} radius={[4,4,0,0]} />
              <Bar dataKey="marjane" fill={colors.marjane} radius={[4,4,0,0]} />
              <Bar dataKey="micromagma" fill={colors.micromagma} radius={[4,4,0,0]} />
              <Bar dataKey="zara" fill={colors.zara} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>🥧 RÉPARTITION PAR PLATEFORME</div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={platformDistribution} cx="50%" cy="50%" innerRadius={40} outerRadius={80} dataKey="value" label={({ name }) => name}>
                {platformDistribution.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* LIGNE 4: Graphique en lignes (temps réel) + Scatter */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>📈 PRIX EN TEMPS RÉEL</div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={lineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a3a50" />
              <XAxis dataKey="name" stroke="#8899bb" tick={{ fontSize: 10 }} />
              <YAxis stroke="#8899bb" tick={{ fontSize: 10 }} tickFormatter={(v) => `${Math.round(v/1000)}k`} />
              <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50' }} formatter={(v) => [`${v.toLocaleString()} MAD`]} />
              <Line type="monotone" dataKey="price" stroke="#00E5FF" strokeWidth={3} dot={{ r: 6, fill: '#00E5FF' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>🎯 DISTRIBUTION DES PRIX (temps réel)</div>
          <ResponsiveContainer width="100%" height={250}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a3a50" />
              <XAxis dataKey="category" stroke="#8899bb" tick={{ fontSize: 10 }} />
              <YAxis dataKey="price" stroke="#8899bb" tick={{ fontSize: 10 }} tickFormatter={(v) => `${Math.round(v/1000)}k`} />
              <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50' }} formatter={(v) => [`${v.toLocaleString()} MAD`]} />
              <Scatter name="Prix" data={scatterData} fill="#FF5C00" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* LIGNE 5: Radial chart (temps réel) + Alertes récentes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>📊 DISTRIBUTION ANNULAIRE (temps réel)</div>
          <ResponsiveContainer width="100%" height={250}>
            <RadialBarChart innerRadius="30%" outerRadius="80%" data={radialData} startAngle={180} endAngle={0}>
              <RadialBar minAngle={15} background clockWise dataKey="value" />
              <Legend iconSize={8} wrapperStyle={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#0d1420', border: '1px solid #2a3a50', fontSize: 10 }} formatter={(v) => `${v.toLocaleString()} MAD`} />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 12, color: '#8899bb', marginBottom: 12 }}>⚠️ ALERTES RÉCENTES</div>
          {recentAlerts.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#4a5a7a' }}>Aucune alerte</div>
          ) : (
            recentAlerts.map((alert, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: idx < 3 ? '1px solid #2a3a50' : 'none' }}>
                <div>
                  <div style={{ fontSize: 11, color: '#fff' }}>{alert.produit?.substring(0, 25)}...</div>
                  <div style={{ fontSize: 9, color: '#4a5a7a' }}>{alert.plateforme} • {alert.categorie}</div>
                </div>
                <div style={{ fontSize: 14, fontWeight: 'bold', color: '#FF5252' }}>{alert.baisse}%</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* LIGNE 6: Mini statistiques */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, textAlign: 'center', border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 10, color: '#8899bb' }}>💰 PRIX MINIMUM</div>
          <div style={{ fontSize: 22, fontWeight: 'bold', color: '#00E676' }}>{Math.round(minPrice).toLocaleString()} MAD</div>
          <div style={{ fontSize: 9, color: '#4a5a7a' }}>le moins cher trouvé</div>
        </div>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, textAlign: 'center', border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 10, color: '#8899bb' }}>💎 PRIX MAXIMUM</div>
          <div style={{ fontSize: 22, fontWeight: 'bold', color: '#FF5252' }}>{Math.round(maxPrice).toLocaleString()} MAD</div>
          <div style={{ fontSize: 9, color: '#4a5a7a' }}>le plus cher trouvé</div>
        </div>
        <div style={{ background: '#162035', borderRadius: 16, padding: 16, textAlign: 'center', border: '1px solid #2a3a50' }}>
          <div style={{ fontSize: 10, color: '#8899bb' }}>📊 NOMBRE DE CATÉGORIES</div>
          <div style={{ fontSize: 22, fontWeight: 'bold', color: '#FFC107' }}>4</div>
          <div style={{ fontSize: 9, color: '#4a5a7a' }}>Smartphones • Laptops • TV • Vêtements</div>
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