import type { Table } from '../../../../types';
import styles from './TableTile.module.css';

interface TableTileProps {
  table: Table;
  onClick: () => void;
}

export function TableTile({ table, onClick }: TableTileProps) {
  const isOccupied = table.occupied;
  let isWarning = false;
  let dwellText = '';

  if (isOccupied && table.seatedTime) {
    const elapsedMinutes = Math.floor((Date.now() - table.seatedTime) / 60000);
    const hrs = Math.floor(elapsedMinutes / 60);
    const mins = elapsedMinutes % 60;
    dwellText = `${hrs}h ${mins}m`;

    if (elapsedMinutes >= 90) {
      isWarning = true;
    }
  }

  const tileClass = isOccupied
    ? `${styles.tableTile} ${styles.occupied} ${isWarning ? styles.warning : ''}`
    : `${styles.tableTile} ${styles.empty}`;

  return (
    <div className={tileClass} onClick={onClick}>
      <div className={`${styles.tileCode} clash`}>{table.id}</div>
      <div className={styles.tileStatus}>
        <div className={styles.tileDot}></div>
        <span>{isOccupied ? `${table.pplCount} ppl` : 'Empty'}</span>
      </div>
      {isOccupied ? (
        <div className={styles.tileMeta} style={{ textTransform: 'capitalize', marginBottom: '4px' }}>
          {table.custType}
        </div>
      ) : (
        <div className={styles.tileMeta}>Cap: {table.cap}</div>
      )}
      {isOccupied ? (
        <div className={styles.tileDwell} style={{ marginTop: 'auto' }}>
          {dwellText}
        </div>
      ) : (
        <div className={styles.tileInviteIcon} style={{ marginTop: 'auto', fontSize: '14px', color: 'rgba(230, 211, 163, 0.25)', fontWeight: 300 }}>
          ⊕
        </div>
      )}
    </div>
  );
}
