import { useState, useEffect } from 'react';
import { useSessionStore } from '../store/sessionStore';

export function useTableState() {
  const tables = useSessionStore((state) => state.tables);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTick((t) => t + 1);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const occupiedCount = tables.filter((t) => t.occupied).length;
  const totalCount = tables.length;

  return {
    tables,
    occupiedCount,
    totalCount,
    tick
  };
}
