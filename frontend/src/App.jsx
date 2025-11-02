import { useState, useEffect } from 'react'
import './App.css'
import api from './services/api'

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
        <h1>CSE412 Project</h1>
        <div className="status-card">
          <h2>Backend Status</h2>
          {loading ? (
            <p>Checking backend connection...</p>
          ) : (
            <div>
              <p className={backendStatus.status === 'healthy' ? 'status-healthy' : 'status-error'}>
                Status: {backendStatus.status}
              </p>
              <p>{backendStatus.message}</p>
            </div>
          )}
        </div>
        <p className="instructions">
          Edit the backend and frontend to add your implementation details
        </p>
      </header>
    </div>
  )
}

export default App
