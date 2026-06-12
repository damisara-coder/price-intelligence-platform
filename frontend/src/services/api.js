const API_BASE = 'http://localhost:8001/api';

export const api = {
  async getKpis() {
    const res = await fetch(`${API_BASE}/kpis`);
    return res.json();
  },

  async getPrices(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/prices?${query}`);
    return res.json();
  },

  async getStats(category) {
    const url = category 
      ? `${API_BASE}/stats?category_normalized=${category}` 
      : `${API_BASE}/stats`;
    const res = await fetch(url);
    return res.json();
  },

  async getBrands(category) {
    const url = category 
      ? `${API_BASE}/brands?category_normalized=${category}` 
      : `${API_BASE}/brands`;
    const res = await fetch(url);
    return res.json();
  },

  async getAlerts(threshold = -10) {
    const res = await fetch(`${API_BASE}/alerts?min_drop_pct=${threshold}`);
    return res.json();
  },

  async health() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  }
};
export const stream = {
  dashboard: () => {
    return new EventSource('http://localhost:8001/api/stream/dashboard');
  }
};