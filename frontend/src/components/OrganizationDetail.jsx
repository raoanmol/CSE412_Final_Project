import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import EventCard from './EventCard'
import api from '../services/api'
import './OrganizationDetail.css'

function OrganizationDetail({ orgId, onBack }) {
  const [organization, setOrganization] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchOrganizationDetails()
  }, [orgId])

  const fetchOrganizationDetails = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.get(`/organizations/${orgId}`)
      setOrganization(response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching organization details:', err)
      setError('Failed to load organization details. Please try again.')
      setLoading(false)
    }
  }

  const formatTitle = (title) => {
    return title.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const getYearLabel = (year) => {
    const labels = { 1: 'Freshman', 2: 'Sophomore', 3: 'Junior', 4: 'Senior', 5: 'Graduate' }
    return labels[year] || `Year ${year}`
  }

  if (loading) {
    return (
      <div className="org-detail-loading">
        <div className="loading-spinner"></div>
        <p>Loading organization details...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="org-detail-error">
        <p>{error}</p>
        <button onClick={onBack} className="back-btn">
          Back to Organizations
        </button>
      </div>
    )
  }

  if (!organization) {
    return (
      <div className="org-detail-error">
        <p>Organization not found.</p>
        <button onClick={onBack} className="back-btn">
          Back to Organizations
        </button>
      </div>
    )
  }

  return (
    <div className="org-detail-container">
      <button onClick={onBack} className="back-btn">
        ← Back to Organizations
      </button>

      {/* Organization Header */}
      <div className="org-detail-header">
        <h1>{organization.org_name}</h1>
        {organization.org_login && (
          <p className="org-login">@{organization.org_login}</p>
        )}
      </div>

      {/* Stats Overview */}
      <div className="org-stats-grid">
        <div className="stat-card">
          <span className="stat-icon">📅</span>
          <div className="stat-content">
            <span className="stat-number">{organization.event_count || 0}</span>
            <span className="stat-label">Events</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">👥</span>
          <div className="stat-content">
            <span className="stat-number">{organization.member_count || 0}</span>
            <span className="stat-label">Members</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">⭐</span>
          <div className="stat-content">
            <span className="stat-number">{organization.officer_count || 0}</span>
            <span className="stat-label">Officers</span>
          </div>
        </div>
      </div>

      {/* Event Distributions */}
      <div className="distributions-section">
        {/* Event Type Distribution */}
        {organization.event_type_distribution && organization.event_type_distribution.length > 0 && (
          <div className="distribution-card">
            <h2>Event Type Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={organization.event_type_distribution.map(item => ({
                    name: item.event_type === 'in_person' ? 'In Person' :
                          item.event_type === 'online' ? 'Online' : 'Hybrid',
                    value: item.count
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {organization.event_type_distribution.map((entry, index) => {
                    const colors = {
                      'in_person': '#8C1D40',
                      'online': '#FFC627',
                      'hybrid': '#00A3E0'
                    }
                    return <Cell key={`cell-${index}`} fill={colors[entry.event_type] || '#999'} />
                  })}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Event Category Distribution */}
        {organization.category_distribution && organization.category_distribution.length > 0 && (
          <div className="distribution-card">
            <h2>Event Category Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={organization.category_distribution.map(item => ({
                    name: item.category,
                    value: item.count
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {organization.category_distribution.map((entry, index) => {
                    const colors = ['#8C1D40', '#FFC627', '#00A3E0', '#78BE20', '#FF6B35', '#9370DB', '#20B2AA', '#FF1493']
                    return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  })}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Officers Section */}
      <div className="org-section">
        <h2>Officers</h2>
        {organization.officers && organization.officers.length > 0 ? (
          <div className="officers-grid">
            {organization.officers.map((officer) => (
              <div key={officer.student_id} className="officer-card">
                <div className="officer-header">
                  <h3>{officer.student_name}</h3>
                  <span className={`officer-badge ${officer.officer_title}`}>
                    {formatTitle(officer.officer_title)}
                  </span>
                </div>
                <div className="officer-info">
                  <p><strong>Email:</strong> {officer.email}</p>
                  <p><strong>Major:</strong> {officer.major}</p>
                  <p><strong>Year:</strong> {getYearLabel(officer.year)}</p>
                  <p><strong>Joined:</strong> {formatDate(officer.join_date)}</p>
                  <p>
                    <strong>Status:</strong>{' '}
                    <span className={officer.is_active ? 'status-active' : 'status-inactive'}>
                      {officer.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">No officers found.</p>
        )}
      </div>

      {/* Events Section */}
      <div className="org-section">
        <h2>Events ({organization.events?.length || 0})</h2>
        {organization.events && organization.events.length > 0 ? (
          <div className="events-grid">
            {organization.events.map((event) => (
              <EventCard key={event.event_id} event={event} />
            ))}
          </div>
        ) : (
          <p className="no-data">No events found for this organization.</p>
        )}
      </div>
    </div>
  )
}

export default OrganizationDetail
