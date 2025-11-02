import { useState, useEffect } from 'react'
import './App.css'
import api from './services/api'
import EventList from './components/EventList'

function App() {
  const [backendStatus, setBackendStatus] = useState(null)
  const [loading, setLoading] = useState(true)

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
        <h1>ASU Sun Devil Central Events</h1>
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
      <main className="App-main">
        <EventList />
      </main>
    </div>
  )
}

export default App
