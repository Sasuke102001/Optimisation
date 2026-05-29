import { useSessionStore } from './store/sessionStore';
import { Header } from './components/shared/Header/Header';
import { InactiveBanner } from './components/shared/InactiveBanner/InactiveBanner';
import { SessionSetup } from './components/setup/SessionSetup/SessionSetup';
import { FloorLogger } from './components/logger/FloorLogger/FloorLogger';
import { KPIMonitor } from './components/monitor/KPIMonitor/KPIMonitor';
import { ToastRack } from './components/shared/Toast/ToastRack';

function App() {
  const active = useSessionStore((state) => state.session.active);
  const currentScreen = useSessionStore((state) => state.currentScreen);

  return (
    <>
      {!active && <InactiveBanner />}
      {active && <Header />}
      
      {currentScreen === 'setup' && <SessionSetup />}
      {currentScreen === 'logger' && <FloorLogger />}
      {currentScreen === 'monitor' && <KPIMonitor />}

      <ToastRack />
    </>
  );
}

export default App;
