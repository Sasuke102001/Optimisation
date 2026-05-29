import React from 'react';
import { useKPIState } from '../../../hooks/useKPIState';
import { getSignalSource } from '../../../types/constants';
import styles from './SignalRow.module.css';

interface SignalRowProps {
  signalName: string;
  zoneId: string;
  familyId: string;
  isLogged: boolean;
}

export function SignalRow({ signalName, zoneId, familyId, isLogged }: SignalRowProps) {
  const { getIndividualSignalStatus } = useKPIState();
  const source = getSignalSource(signalName);
  const sigStatus = getIndividualSignalStatus(zoneId, familyId, signalName);

  let rightSideNode: React.ReactNode = null;

  if (source === 'manual') {
    if (isLogged) {
      rightSideNode = <div className={`${styles.sigInd} ${styles[sigStatus]}`} />;
    } else {
      rightSideNode = (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '10px', color: 'var(--text-disabled)', fontStyle: 'italic' }}>
            Tap to assess
          </span>
          <div className={`${styles.sigInd} ${styles.sigPulseGrey}`} />
        </div>
      );
    }
  } else {
    rightSideNode = <div className={`${styles.sigInd} ${styles[sigStatus]}`} />;
  }

  const badgeText = source === 'derived' ? 'auto' : source;
  const badgeClass = styles[source];

  return (
    <div className={styles.signalRow}>
      <span className={styles.sigName}>
        {signalName}
        <span className={`${styles.srcBadge} ${badgeClass}`}>
          {badgeText}
        </span>
      </span>
      {rightSideNode}
    </div>
  );
}
