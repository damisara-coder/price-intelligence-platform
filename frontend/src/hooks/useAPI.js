import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function useAPI(fetcher, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    
    fetcher()
      .then(result => {
        if (mounted) {
          setData(result);
          setError(null);
        }
      })
      .catch(err => {
        if (mounted) setError(err.message);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    
    return () => { mounted = false; };
  }, deps);

  return { data, loading, error, refetch: () => {} };
}

export function useKPIs() {
  return useAPI(() => api.getKpis(), []);
}

export function usePrices(params) {
  return useAPI(() => api.getPrices(params), [JSON.stringify(params)]);
}

export function useStats(category) {
  return useAPI(() => api.getStats(category), [category]);
}

export function useBrands(category) {
  return useAPI(() => api.getBrands(category), [category]);
}

export function useAlerts(threshold) {
  return useAPI(() => api.getAlerts(threshold), [threshold]);
}