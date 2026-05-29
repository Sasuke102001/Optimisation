import { useSEStore } from './store/seStore'
import { VenueSelector } from './screens/VenueSelector'
import { PlanGeneration } from './screens/PlanGeneration'
import { ShowPlan } from './screens/ShowPlan'
import { PostShowReview } from './screens/PostShowReview'
import { ShowHistory } from './screens/ShowHistory'
import './App.css'

function App() {
  const { navSection, setNavSection, planScreen, historyScreen, setHistoryScreen } = useSEStore()

  return (
    <div className="app-shell">
      {/* ── Top Nav ── */}
      <header className="app-nav">
        <div className="app-nav-inner">
          <div className="app-nav-brand">
            <span className="app-nav-glyph">✦</span>
            <span className="app-nav-name clash">Show Engineering</span>
            <span className="app-nav-badge">PolyNovea M3</span>
          </div>

          <nav className="app-nav-tabs" role="navigation" aria-label="Main navigation">
            <button
              id="nav-tab-plan"
              className={`app-nav-tab${navSection === 'plan' ? ' active' : ''}`}
              onClick={() => setNavSection('plan')}
            >
              Plan
            </button>
            <button
              id="nav-tab-history"
              className={`app-nav-tab${navSection === 'history' ? ' active' : ''}`}
              onClick={() => setNavSection('history')}
            >
              History
            </button>
          </nav>

          {/* History sub-tabs (only visible in history section) */}
          {navSection === 'history' && (
            <div className="app-nav-subtabs">
              <button
                id="nav-subtab-review"
                className={`app-nav-subtab${historyScreen === 'post_show_review' ? ' active' : ''}`}
                onClick={() => setHistoryScreen('post_show_review')}
              >
                Post-Show Review
              </button>
              <button
                id="nav-subtab-history"
                className={`app-nav-subtab${historyScreen === 'show_history' ? ' active' : ''}`}
                onClick={() => setHistoryScreen('show_history')}
              >
                Prior Shows
              </button>
            </div>
          )}
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="app-main">
        {navSection === 'plan' && (
          <>
            {planScreen === 'venue_selector'  && <VenueSelector />}
            {planScreen === 'plan_generation' && <PlanGeneration />}
            {planScreen === 'show_plan'       && <ShowPlan />}
          </>
        )}
        {navSection === 'history' && (
          <>
            {historyScreen === 'post_show_review' && <PostShowReview />}
            {historyScreen === 'show_history'     && <ShowHistory />}
          </>
        )}
      </main>
    </div>
  )
}

export default App
