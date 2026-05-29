import { useState, useEffect } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import styles from './TableStepper.module.css';

export function TableStepper() {
  const { tableConfig, adjustTableType } = useSessionStore();
  const [flashTwo, setFlashTwo] = useState(false);
  const [flashFour, setFlashFour] = useState(false);
  const [flashSix, setFlashSix] = useState(false);

  useEffect(() => {
    if (tableConfig.two > 0) {
      setFlashTwo(true);
      const timer = setTimeout(() => setFlashTwo(false), 600);
      return () => clearTimeout(timer);
    }
  }, [tableConfig.two]);

  useEffect(() => {
    if (tableConfig.four > 0) {
      setFlashFour(true);
      const timer = setTimeout(() => setFlashFour(false), 600);
      return () => clearTimeout(timer);
    }
  }, [tableConfig.four]);

  useEffect(() => {
    if (tableConfig.six > 0) {
      setFlashSix(true);
      const timer = setTimeout(() => setFlashSix(false), 600);
      return () => clearTimeout(timer);
    }
  }, [tableConfig.six]);

  const total = tableConfig.two + tableConfig.four + tableConfig.six;

  return (
    <div className={styles.setupField} id="table-config-section">
      <div className={styles.setupLbl}>
        Table Layout <span className={styles.lblSub}>— set once per venue, remembered automatically</span>
      </div>
      <div className={styles.setupStepperGrid}>
        <div className={`${styles.stepperCol} ${flashTwo ? styles.flashGreenActive : ''}`}>
          <div className={styles.stepperLabel}>2-person</div>
          <div className={styles.stepperControls}>
            <button type="button" className={styles.stepperBtn} onClick={() => adjustTableType('two', -1)}>−</button>
            <span className={styles.stepperValLarge}>{tableConfig.two}</span>
            <button type="button" className={styles.stepperBtn} onClick={() => adjustTableType('two', 1)}>+</button>
          </div>
        </div>
        <div className={`${styles.stepperCol} ${flashFour ? styles.flashGreenActive : ''}`}>
          <div className={styles.stepperLabel}>4-person</div>
          <div className={styles.stepperControls}>
            <button type="button" className={styles.stepperBtn} onClick={() => adjustTableType('four', -1)}>−</button>
            <span className={styles.stepperValLarge}>{tableConfig.four}</span>
            <button type="button" className={styles.stepperBtn} onClick={() => adjustTableType('four', 1)}>+</button>
          </div>
        </div>
        <div className={`${styles.stepperCol} ${flashSix ? styles.flashGreenActive : ''}`}>
          <div className={styles.stepperLabel}>6-person</div>
          <div className={styles.stepperControls}>
            <button type="button" className={styles.stepperBtn} onClick={() => adjustTableType('six', -1)}>−</button>
            <span className={styles.stepperValLarge}>{tableConfig.six}</span>
            <button type="button" className={styles.stepperBtn} onClick={() => adjustTableType('six', 1)}>+</button>
          </div>
        </div>
      </div>
      <div className={styles.totalDisplay}>
        Total: <span>{total}</span> tables
      </div>
    </div>
  );
}
