import { useState, useEffect } from 'react'
import OrganizationCard from './OrganizationCard'
import api from '../services/api'
import './OrganizationList.css'

function OrganizationList({ onOrganizationClick }) {
  const [organizations, setOrganizations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('name')

  useEffect(() => {
    fetchOrganizations()
  }, [searchTerm, sortBy])

  const fetchOrganizations = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = {
        with_stats: 'true',
      }

      if (searchTerm) {
        params.search = searchTerm
      }

      if (sortBy) {
        params.sort_by = sortBy
      }

      const response = await api.get('/organizations', { params })
      setOrganizations(response.data.organizations || [])
      setLoading(false)
    } catch (err) {
      console.error('Error fetching organizations:', err)
      setError('Failed to load organizations. Please try again.')
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setError(null)
    fetchOrganizations()
  }

  if (error) {
    return (
      <div className="org-list-error">
        <p>{error}</p>
        <button onClick={handleRetry} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="org-list-container">
      <div className="org-list-header">
        <h2>ASU Organizations</h2>
        <p className="org-count">
          {organizations.length} organization{organizations.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="org-filters">
        {/* Search Box */}
        <div className="filter-item filter-search">
          <label htmlFor="org-search">Search Organizations</label>
          <input
            id="org-search"
            type="text"
            placeholder="Search by organization name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Sort Dropdown */}
        <div className="filter-item">
          <label htmlFor="sort-by">Sort By</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="name">Name (A-Z)</option>
            <option value="events">Most Events</option>
            <option value="members">Most Members</option>
            <option value="officers">Most Officers</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading organizations...</p>
        </div>
      ) : (
        <>
          <div className="org-grid">
            {organizations.map((org) => (
              <OrganizationCard
                key={org.org_id}
                organization={org}
                onClick={onOrganizationClick}
              />
            ))}
          </div>

          {organizations.length === 0 && !loading && (
            <div className="no-results">
              <p>No organizations found.</p>
              {searchTerm && (
                <p className="suggestion">Try adjusting your search term.</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default OrganizationList
