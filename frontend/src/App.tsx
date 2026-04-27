import { useState } from 'react'
import LawView from './pages/LawView'
import GraphView from './pages/GraphView'
import TaxsimView from './pages/TaxsimView'
import TaxFormView from './pages/TaxFormView'
import './App.css'

type MainView = 'law' | 'graph' | 'taxsim' | 'forms'

function App() {
  const [mainView, setMainView] = useState<MainView>('law')

  return (
    <div className="App flex flex-col h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              26 U.S.C. § 199A
              <span className="text-slate-400 font-normal ml-2">|</span>
              <span className="text-slate-600 font-normal ml-2">Qualified Business Income Deduction</span>
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">
              PolicyEngine US Implementation Visualizer
            </p>
          </div>
          <div className="flex gap-1 bg-slate-100 p-1 rounded-lg">
            <button
              onClick={() => setMainView('law')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                mainView === 'law'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Law Structure
            </button>
            <button
              onClick={() => setMainView('graph')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                mainView === 'graph'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Code Graph
            </button>
            <button
              onClick={() => setMainView('taxsim')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                mainView === 'taxsim'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              TAXSIM Comparison
            </button>
            <button
              onClick={() => setMainView('forms')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                mainView === 'forms'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Tax Forms
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        {mainView === 'law' && <LawView />}
        {mainView === 'graph' && <GraphView />}
        {mainView === 'taxsim' && <TaxsimView />}
        {mainView === 'forms' && <TaxFormView />}
      </main>
    </div>
  )
}

export default App
