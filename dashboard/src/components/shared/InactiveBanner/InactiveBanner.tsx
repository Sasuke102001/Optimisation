import styles from './InactiveBanner.module.css';

export function InactiveBanner() {
  return (
    <div className={styles.inactiveBanner}>
      <span className={styles.inactiveLogo}>PN</span>
      <span>No active session — open a session to start logging.</span>
    </div>
  );
}
