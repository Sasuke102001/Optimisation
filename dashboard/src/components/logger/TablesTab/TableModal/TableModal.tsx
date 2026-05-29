import { useState, useEffect } from 'react';
import type { MouseEvent } from 'react';
import { useSessionStore } from '../../../../store/sessionStore';
import { SegmentedControl } from '../../../shared/SegmentedControl/SegmentedControl';
import { showToast } from '../../../shared/Toast/ToastRack';
import type { Table } from '../../../../types';
import styles from './TableModal.module.css';

interface TableModalProps {
  table: Table;
  onClose: () => void;
}

export function TableModal({ table, onClose }: TableModalProps) {
  const { saveTableAction, clearTableAction } = useSessionStore();
  const [pplCount, setPplCount] = useState<number | '6+' | null>(null);
  const [custType, setCustType] = useState<string | null>(null);
  const [note, setNote] = useState('');

  // Load values when table updates or modal opens
  useEffect(() => {
    if (table) {
      setPplCount(table.pplCount);
      setCustType(table.custType);
      setNote(table.note || '');
    }
  }, [table]);

  const handleOverlayClick = (e: MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSave = () => {
    if (!pplCount) {
      showToast('Please select headcount first', 'warn');
      return;
    }
    if (!custType) {
      showToast('Please select customer type first', 'warn');
      return;
    }

    saveTableAction(table.id, pplCount, custType, note.trim());
    showToast(`${table.id} updated`, 'ok');
    onClose();
  };

  const handleClear = () => {
    const res = clearTableAction(table.id);
    if (res) {
      showToast(`${table.id} cleared — ${res.dwellText} dwell`, 'ok');
    } else {
      showToast(`${table.id} cleared`, 'ok');
    }
    onClose();
  };

  const pplOptions = [
    { label: '1', value: 1 },
    { label: '2', value: 2 },
    { label: '3', value: 3 },
    { label: '4', value: 4 },
    { label: '5', value: 5 },
    { label: '6+', value: '6+' }
  ];

  const segments = ['Couple', 'Social Group', 'Family', 'College', 'Corporate', 'Solo', 'Mixed'];

  return (
    <div className={styles.modalOverlay} onClick={handleOverlayClick}>
      <div className={styles.modalContainer}>
        <div className={styles.modalHead}>
          <div>
            <div className={styles.modalTitle}>Table {table.id}</div>
            <div className={styles.modalCap} id="table-modal-cap">
              Capacity: {table.cap}
            </div>
          </div>
          <button type="button" className={styles.modalClose} onClick={onClose}>
            ✕
          </button>
        </div>

        <div className={styles.setupField}>
          <div className={styles.setupLbl}>How many people?</div>
          <SegmentedControl
            options={pplOptions}
            value={pplCount}
            onChange={(val) => setPplCount(val)}
            id="table-ppl-ctrl"
            style={{ height: '44px' }}
          />
        </div>

        <div className={styles.setupField}>
          <div className={styles.setupLbl}>Customer type?</div>
          <div className={styles.chipGrid} id="table-segment-ctrl">
            {segments.map((seg) => (
              <button
                key={seg}
                type="button"
                className={`${styles.chip} ${custType === seg ? styles.active : ''}`}
                onClick={() => setCustType(seg)}
              >
                {seg}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.setupField}>
          <div className={styles.setupLbl}>Behavioural note (optional)</div>
          <input
            className={styles.setupInput}
            id="table-note-input"
            type="text"
            placeholder="Add behavioral observations..."
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          {table.occupied && (
            <button
              type="button"
              className="btn btn-ghost"
              id="table-clear-btn"
              style={{ flex: 1, padding: '12px' }}
              onClick={handleClear}
            >
              Clear Table
            </button>
          )}
          <button
            type="button"
            className="btn btn-gold"
            id="table-save-btn"
            style={{ flex: table.occupied ? 1.5 : 1, padding: '12px', fontWeight: 700 }}
            onClick={handleSave}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
