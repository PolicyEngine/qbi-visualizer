import { useState } from 'react'
import CalculatorView from './pages/CalculatorView'
import LawView from './pages/LawView'
import GraphView from './pages/GraphView'
import TaxsimView from './pages/TaxsimView'
import TaxFormView from './pages/TaxFormView'
import './App.css'

type MainView = 'calculator' | 'law' | 'graph' | 'taxsim' | 'forms'

function App() {
  const [mainView, setMainView] = useState<MainView>('calculator')

  const tabs: { id: MainView; label: string }[] = [
    { id: 'calculator', label: 'QBID Calculator' },
    { id: 'law', label: 'Law Structure' },
    { id: 'graph', label: 'Code Graph' },
    { id: 'taxsim', label: 'TAXSIM Comparison' },
    { id: 'forms', label: 'Tax Forms' },
  ]

  return (
    <div className="App flex flex-col h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              26 U.S.C. &sect; 199A
              <span className="text-slate-400 font-normal ml-2">|</span>
              <span className="text-slate-600 font-normal ml-2">Qualified Business Income Deduction</span>
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">
              PolicyEngine US &middot; Interactive Calculator &amp; Implementation Explorer
            </p>
          </div>
          <div className="flex gap-1 bg-slate-100 p-1 rounded-lg">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setMainView(tab.id)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  mainView === tab.id
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
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
        {mainView === 'graph' && <GraphView />}
        {mainView === 'taxsim' && <TaxsimView />}
        {mainView === 'forms' && <TaxFormView />}
      </main>
    </div>
  )
}

export default App
