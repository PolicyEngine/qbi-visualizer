import { useEffect, useState } from 'react'
import CalculatorView from './pages/CalculatorView'
import LawView from './pages/LawView'
import TaxFormView from './pages/TaxFormView'
import './App.css'

type MainView = 'calculator' | 'law' | 'forms'

// Law structure and Tax forms are reachable only via URL hash
// (#/law, #/forms) — the calculator is the default and the only
// view advertised in the header tab strip.
const viewFromHash = (): MainView => {
  const h = window.location.hash.replace(/^#\/?/, '');
  if (h === 'law') return 'law';
  if (h === 'forms') return 'forms';
  return 'calculator';
};

function App() {
  const [mainView, setMainView] = useState<MainView>(viewFromHash);

  useEffect(() => {
    const onHashChange = () => setMainView(viewFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const tabs: { id: MainView; label: string }[] = [
    { id: 'calculator', label: 'QBID calculator' },
  ];

  return (
    <div className="App flex flex-col h-screen bg-pe-bg-primary">
      <header className="bg-white border-b border-pe-gray-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <img
              src="https://raw.githubusercontent.com/PolicyEngine/policyengine-app-v2/main/app/public/assets/logos/policyengine/teal.png"
              alt="PolicyEngine"
              className="h-8"
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
          <div className="flex gap-1 bg-pe-gray-100 p-1 rounded-pe-lg">
            {tabs.map((tab) => (
              <button
                key={tab.id}
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
      </main>
    </div>
  )
}

export default App
