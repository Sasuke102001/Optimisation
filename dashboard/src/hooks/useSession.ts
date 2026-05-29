import { useState, useEffect } from 'react';
import { useSessionStore } from '../store/sessionStore';

export function useSession() {
  const session = useSessionStore((state) => state.session);
  const [timerText, setTimerText] = useState('00:00');

  useEffect(() => {
    if (!session.active || !session.startTime) {
      setTimerText('00:00');
      return;
    }

    const updateTimer = () => {
      if (!session.startTime) return;
      const diffSecs = Math.floor((Date.now() - session.startTime) / 1000);
      const mins = String(Math.floor(diffSecs / 60)).padStart(2, '0');
      const secs = String(diffSecs % 60).padStart(2, '0');
      setTimerText(`${mins}:${secs}`);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [session.active, session.startTime]);

  return {
    timerText,
    session,
  };
}
