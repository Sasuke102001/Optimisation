import { useState } from 'react';
import { useTableState } from '../../../hooks/useTableState';
import { TableTile } from './TableTile/TableTile';
import { TableModal } from './TableModal/TableModal';
import type { Table } from '../../../types';
import styles from './TablesTab.module.css';

export function TablesTab() {
  const { tables, occupiedCount, totalCount } = useTableState();
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);

  const handleTileSelect = (table: Table) => {
    setSelectedTable(table);
  };

  // Keep selectedTable reference updated with state changes (e.g. if edited or cleared)
  const currentSelectedTable = selectedTable
    ? tables.find((t) => t.id === selectedTable.id) || null
    : null;

  return (
    <div className={styles.tablesTab}>
      <div className={styles.tableHeaderRow}>
        <span className={styles.tableGridTitle} id="table-grid-title">
          Venue Table Grid
        </span>
        <span className={styles.tableSummaryStats} id="table-summary-stats">
          Occupied: {occupiedCount}/{totalCount}
        </span>
      </div>

      <div className={styles.tableGrid} id="tables-grid-container">
        {tables.map((t) => (
          <TableTile key={t.id} table={t} onClick={() => handleTileSelect(t)} />
        ))}
      </div>

      {currentSelectedTable && (
        <TableModal
          table={currentSelectedTable}
          onClose={() => setSelectedTable(null)}
        />
      )}
    </div>
  );
}
