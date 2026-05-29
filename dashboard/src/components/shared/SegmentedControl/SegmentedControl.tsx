import React from 'react';
import styles from './SegmentedControl.module.css';

interface Option {
  label: string;
  value: any;
}

interface SegmentedControlProps {
  options: (string | Option)[];
  value: any;
  onChange: (value: any) => void;
  id?: string;
  style?: React.CSSProperties;
  className?: string;
}

export function SegmentedControl({ options, value, onChange, id, style, className = '' }: SegmentedControlProps) {
  return (
    <div className={`${styles.segmentedControl} ${className}`} id={id} style={style}>
      {options.map((opt, idx) => {
        const optionLabel = typeof opt === 'string' ? opt : opt.label;
        const optionValue = typeof opt === 'string' ? opt : opt.value;
        const isActive = optionValue === value;
        return (
          <button
            key={idx}
            type="button"
            className={isActive ? styles.active : ''}
            onClick={() => onChange(optionValue)}
          >
            {optionLabel}
          </button>
        );
      })}
    </div>
  );
}
