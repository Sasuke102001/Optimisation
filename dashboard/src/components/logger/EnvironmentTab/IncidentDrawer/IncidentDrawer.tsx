import React, { useState } from 'react';
import { useSessionStore } from '../../../../store/sessionStore';
import { SegmentedControl } from '../../../shared/SegmentedControl/SegmentedControl';
import { showToast } from '../../../shared/Toast/ToastRack';
import styles from './IncidentDrawer.module.css';

interface IncidentDrawerProps {
  onClose: () => void;
}

export function IncidentDrawer({ onClose }: IncidentDrawerProps) {
  const { submitIncidentAction } = useSessionStore();

  const [type, setType] = useState('Excessive Noise');
  const [severity, setSeverity] = useState<'watch' | 'alert'>('watch');
  const [zone, setZone] = useState('entrance');
  const [note, setNote] = useState('');

  const typesList = [
    { label: 'Noise', value: 'Excessive Noise' },
    { label: 'Crowd', value: 'Overcrowding' },
    { label: 'Service Refusal', value: 'Service Refusal' },
    { label: 'Safety', value: 'Safety Concern' },
    { label: 'Temp Comfort', value: 'Temperature Comfort' },
    { label: 'Other', value: 'Other' }
  ];

  const severityOptions = [
    { label: 'Moderate', value: 'watch' as const },
    { label: 'High', value: 'alert' as const }
  ];

  const zoneOptions = [
    { label: 'Entrance', value: 'entrance' },
    { label: 'Queue', value: 'queue' },
    { label: 'Bar', value: 'main_bar' },
    { label: 'Floor', value: 'dancefloor' }
  ];

  const handleSubmit = () => {
    submitIncidentAction(type, severity, zone, note.trim());
    showToast('Complaint logged', 'ok');
    onClose();
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.drawerOverlay} onClick={handleOverlayClick}>
      <div className={styles.drawer}>
        <div className={styles.drawerHead}>
          <div className={styles.drawerTitle}>🚨 Log Complaint / Incident</div>
          <button type="button" className={styles.modalClose} onClick={onClose}>
            ✕
          </button>
        </div>
        <div className={styles.drawerBody}>
          <div className={styles.setupField}>
            <div className={styles.setupLbl}>Incident Type</div>
            <div className={styles.chipGrid} id="incident-type-ctrl">
              {typesList.map((t) => (
                <button
                  key={t.value}
                  type="button"
                  className={`${styles.chip} ${type === t.value ? styles.active : ''}`}
                  onClick={() => setType(t.value)}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.setupField}>
            <div className={styles.setupLbl}>Severity</div>
            <SegmentedControl
              options={severityOptions}
              value={severity}
              onChange={(val) => setSeverity(val)}
              id="incident-sev-ctrl"
            />
          </div>

          <div className={styles.setupField}>
            <div className={styles.setupLbl}>Associated Zone</div>
            <SegmentedControl
              options={zoneOptions}
              value={zone}
              onChange={(val) => setZone(val)}
              id="incident-zone-ctrl"
              style={{ flexWrap: 'wrap', height: 'auto' }}
            />
          </div>

          <div className={styles.setupField}>
            <div className={styles.setupLbl}>Incident Details</div>
            <textarea
              className={styles.setupInput}
              id="incident-note-input"
              rows={4}
              style={{ resize: 'none', height: 'auto' }}
              placeholder="Explain what is happening..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </div>

          <button
            type="button"
            className="btn btn-gold"
            style={{ width: '100%', height: '44px', marginTop: '10px' }}
            onClick={handleSubmit}
          >
            Submit Complaint →
          </button>
        </div>
      </div>
    </div>
  );
}
