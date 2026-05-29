import { useSessionStore } from '../../../store/sessionStore';
import { DoorFlow } from '../DoorFlow/DoorFlow';
import { TablesTab } from '../TablesTab/TablesTab';
import { EnvironmentTab } from '../EnvironmentTab/EnvironmentTab';
import styles from './FloorLogger.module.css';

export function FloorLogger() {
  const { currentLoggerTab, switchLoggerTab } = useSessionStore();

  return (
    <div className={styles.loggerScreen} id="screen-logger">
      <nav className={styles.loggerTabs}>
        <button
          className={`${styles.ltab} ${currentLoggerTab === 'flow' ? styles.active : ''}`}
          onClick={() => switchLoggerTab('flow')}
        >
          Door &amp; Flow
        </button>
        <button
          className={`${styles.ltab} ${currentLoggerTab === 'tables' ? styles.active : ''}`}
          onClick={() => switchLoggerTab('tables')}
        >
          Tables
        </button>
        <button
          className={`${styles.ltab} ${currentLoggerTab === 'env' ? styles.active : ''}`}
          onClick={() => switchLoggerTab('env')}
        >
          Environment
        </button>
      </nav>

      <div className={styles.loggerContainer}>
        <div className={`${styles.tabPanel} ${currentLoggerTab === 'flow' ? styles.active : ''}`}>
          <DoorFlow />
        </div>
        <div className={`${styles.tabPanel} ${currentLoggerTab === 'tables' ? styles.active : ''}`}>
          <TablesTab />
        </div>
        <div className={`${styles.tabPanel} ${currentLoggerTab === 'env' ? styles.active : ''}`}>
          <EnvironmentTab />
        </div>
      </div>
    </div>
  );
}
