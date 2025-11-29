import { useState, useEffect } from 'react'
import './App.css'
import api from './services/api'
import EventList from './components/EventList'
import OrganizationList from './components/OrganizationList'

function App() {
  const [backendStatus, setBackendStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('events')

  useEffect(() => {
    checkBackendHealth()
  }, [])

  const checkBackendHealth = async () => {
    try {
      const response = await api.get('/health')
      setBackendStatus(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Backend connection failed:', error)
      setBackendStatus({ status: 'error', message: 'Failed to connect to backend' })
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>ASU Sun Devil Central</h1>
        <div className="status-indicator">
          {loading ? (
            <span className="status-loading">Checking connection...</span>
          ) : (
            <span className={backendStatus.status === 'healthy' ? 'status-healthy' : 'status-error'}>
              {backendStatus.status === 'healthy' ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
          )}
        </div>
      </header>

      <nav className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          Events
        </button>
        <button
          className={`tab-button ${activeTab === 'organizations' ? 'active' : ''}`}
          onClick={() => setActiveTab('organizations')}
        >
          Organizations
        </button>
      </nav>

      <main className="App-main">
        {activeTab === 'events' ? <EventList /> : <OrganizationList />}
      </main>
    </div>
  )
}

export default App
