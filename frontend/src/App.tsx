import { useEffect, useState } from 'react'
import CalculatorView from './pages/CalculatorView'
import LawView from './pages/LawView'
import TaxFormView from './pages/TaxFormView'
import NotFound from './pages/NotFound'
import './App.css'

type MainView = 'calculator' | 'law' | 'forms' | 'not_found'

// Law structure and Tax forms are reachable only via URL path (/law, /forms)
// — the calculator is the default and the only view advertised in the
// header tab strip. Path-based routing (rather than hash) is required so
// crawlers and link-preview bots see distinct URLs.
const viewFromPath = (): MainView => {
  const p = window.location.pathname.replace(/\/+$/, '') || '/';
  if (p === '/' || p === '') return 'calculator';
  if (p === '/law') return 'law';
  if (p === '/forms') return 'forms';
  return 'not_found';
};

function App() {
  const [mainView, setMainView] = useState<MainView>(viewFromPath);

  useEffect(() => {
    const onPopState = () => setMainView(viewFromPath());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  // Per-route page <title> so each path gets a distinct title for
  // social shares and browser tabs.
  useEffect(() => {
    const base = 'QBI Deduction Calculator (IRC §199A) | PolicyEngine';
    const titles: Record<MainView, string> = {
      calculator: base,
      law: `Law structure | ${base}`,
      forms: `Tax forms | ${base}`,
      not_found: `Not found | ${base}`,
    };
    document.title = titles[mainView];
  }, [mainView]);

  const tabs: { id: MainView; label: string }[] = [
    { id: 'calculator', label: 'QBID calculator' },
  ];

  return (
    <div className="App flex flex-col h-screen bg-pe-bg-primary">
      <header className="bg-white border-b border-pe-gray-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <img
              src="/policyengine-logo.png"
              alt="PolicyEngine"
              width={154}
              height={32}
              className="h-8 w-auto"
            />
            <div className="border-l border-pe-gray-200 pl-4">
              <h1 className="text-lg font-semibold text-pe-text-primary">
                Qualified Business Income Deduction
              </h1>
              <p className="text-xs text-pe-text-tertiary">
                26 U.S.C. &sect; 199A
              </p>
            </div>
          </div>
          <div role="tablist" aria-label="Application views" className="flex gap-1 bg-pe-gray-100 p-1 rounded-pe-lg">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                role="tab"
                aria-selected={mainView === tab.id}
                onClick={() => setMainView(tab.id)}
                className={`px-4 py-2 rounded-pe-md text-sm font-medium transition-all ${
                  mainView === tab.id
                    ? 'bg-white text-pe-text-primary shadow-sm'
                    : 'text-pe-text-secondary hover:text-pe-text-primary'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        {mainView === 'calculator' && <CalculatorView />}
        {mainView === 'law' && <LawView />}
        {mainView === 'forms' && <TaxFormView />}
        {mainView === 'not_found' && <NotFound />}
      </main>
    </div>
  )
}

export default App
