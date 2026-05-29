import styles from './Badge.module.css';

interface BadgeProps {
  type: 'mode' | 'status';
  value: string;
  className?: string;
}

export function Badge({ type, value, className = '' }: BadgeProps) {
  const normValue = value.toLowerCase();
  
  if (type === 'mode') {
    let displayVal = value;
    if (normValue === 'baseline') displayVal = 'Baseline';
    else if (normValue === 'engineered') displayVal = 'Engineered';
    else if (normValue === 'followup') displayVal = 'Follow-up';

    return (
      <span className={`${styles.badge} ${styles[`badge-${normValue.replace('-', '')}`]} ${className}`}>
        {displayVal}
      </span>
    );
  } else {
    let label = value;
    if (normValue === 'ok') label = 'Normal';
    else if (normValue === 'watch') label = 'Watch';
    else if (normValue === 'alert') label = 'Alert';
    else if (normValue === 'stale') label = 'Stale';
    else if (normValue === 'none') label = 'Unlogged';

    return (
      <span className={`${styles.statusBadge} ${styles[`st-${normValue}`]} ${className}`}>
        {label}
      </span>
    );
  }
}
