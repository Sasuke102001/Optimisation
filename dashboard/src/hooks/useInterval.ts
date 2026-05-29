import { useEffect } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { showToast } from '../components/shared/Toast/ToastRack';

export function useInterval() {
  const active = useSessionStore((state) => state.session.active);
  const interval = useSessionStore((state) => state.session.interval);
  const timeRemaining = useSessionStore((state) => state.intervalTimeRemaining);
  const decrement = useSessionStore((state) => state.decrementIntervalTime);
  const reset = useSessionStore((state) => state.resetIntervalTime);

  useEffect(() => {
    if (!active) return;

    const ticker = setInterval(() => {
      // Access current value to check if expired
      const curRemaining = useSessionStore.getState().intervalTimeRemaining;
      if (curRemaining <= 0) {
        showToast('⏱ Interval finished — Submit interval counts now', 'warn');
        reset();
      } else {
        decrement();
      }
    }, 1000);

    return () => clearInterval(ticker);
  }, [active, decrement, reset]);

  // Formatted remaining time MM:SS
  const mins = String(Math.floor(timeRemaining / 60)).padStart(2, '0');
  const secs = String(timeRemaining % 60).padStart(2, '0');
  const formatted = `${mins}:${secs}`;

  const pct = Math.max(0, Math.min(100, (timeRemaining / (interval * 60)) * 100));

  // RAG status
  let status: 'normal' | 'warning' | 'danger' = 'normal';
  if (timeRemaining <= 0) {
    status = 'danger';
  } else if (timeRemaining <= 120) {
    status = 'warning';
  }

  return {
    timeRemaining,
    formatted,
    pct,
    status
  };
}
