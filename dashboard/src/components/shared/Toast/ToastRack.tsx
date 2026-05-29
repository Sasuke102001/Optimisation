import { useState, useEffect } from 'react';
import styles from './Toast.module.css';

interface ToastItem {
  id: number;
  msg: string;
  type: 'ok' | 'warn' | 'alert';
}

let toastListener: ((msg: string, type: 'ok' | 'warn' | 'alert') => void) | null = null;

export function showToast(msg: string, type: 'ok' | 'warn' | 'alert' = 'ok') {
  if (toastListener) {
    toastListener(msg, type);
  }
}

export function ToastRack() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    toastListener = (msg, type) => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev, { id, msg, type }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 2750);
    };
    return () => {
      toastListener = null;
    };
  }, []);

  return (
    <div className={styles.toastRack}>
      {toasts.map((t) => {
        let cleanMsg = t.msg;
        if (t.msg.startsWith('✓') || t.msg.startsWith('⚠') || t.msg.startsWith('🚨') || t.msg.startsWith('⏱')) {
          cleanMsg = t.msg.substring(1).trim();
        }
        const icon = t.type === 'ok' ? '✓' : t.type === 'warn' ? '⚠' : '🚨';
        return (
          <div key={t.id} className={`${styles.toast} ${styles[t.type]}`}>
            <span>{icon}</span> {cleanMsg}
          </div>
        );
      })}
    </div>
  );
}
