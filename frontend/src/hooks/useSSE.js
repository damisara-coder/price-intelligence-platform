import { useState, useEffect } from 'react';

export function useSSE(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(url);
    
    eventSource.onopen = () => setConnected(true);
    eventSource.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        setData(newData);
      } catch (e) {}
    };
    eventSource.onerror = () => setConnected(false);
    
    return () => eventSource.close();
  }, [url]);

  return { data, connected };
}