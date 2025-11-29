import { useState, useEffect } from 'react'
import MultiSelectDropdown from './MultiSelectDropdown'
import api from '../services/api'
import './FilterBar.css'

function FilterBar({ onFilterChange }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategories, setSelectedCategories] = useState([])
  const [selectedOrganizations, setSelectedOrganizations] = useState([])
  const [selectedEventType, setSelectedEventType] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const [categories, setCategories] = useState([])
  const [organizations, setOrganizations] = useState([])
  const [loading, setLoading] = useState(true)

  // Fetch categories and organizations
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        setLoading(true)
        const [categoriesRes, organizationsRes] = await Promise.all([
          api.get('/categories'),
          api.get('/organizations')
        ])

        setCategories(categoriesRes.data.categories || [])
        setOrganizations(organizationsRes.data.organizations || [])
      } catch (error) {
        console.error('Error fetching filter options:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchFilterOptions()
  }, [])

  // Notify parent component whenever filters change
  useEffect(() => {
    const filters = {
      search: searchTerm || null,
      category: selectedCategories.length > 0 ? selectedCategories : null,
      organization: selectedOrganizations.length > 0 ? selectedOrganizations.map(org => org.org_id) : null,
      event_type: selectedEventType || null,
      start_date: startDate || null,
      end_date: endDate || null
    }

    onFilterChange(filters)
  }, [searchTerm, selectedCategories, selectedOrganizations, selectedEventType, startDate, endDate, onFilterChange])

  const handleClearAll = () => {
    setSearchTerm('')
    setSelectedCategories([])
    setSelectedOrganizations([])
    setSelectedEventType('')
    setStartDate('')
    setEndDate('')
  }

  const hasActiveFilters = searchTerm || selectedCategories.length > 0 ||
    selectedOrganizations.length > 0 || selectedEventType || startDate || endDate

  if (loading) {
    return <div className="filter-bar-loading">Loading filters...</div>
  }

  return (
    <div className="filter-bar">
      <div className="filter-bar-header">
        <h3>Filter Events</h3>
        {hasActiveFilters && (
          <button className="clear-filters-btn" onClick={handleClearAll}>
            Clear All Filters
          </button>
        )}
      </div>

      <div className="filter-grid">
        {/* Search Box */}
        <div className="filter-item filter-search">
          <label htmlFor="search">Search Events</label>
          <input
            id="search"
            type="text"
            placeholder="Search by event name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Category Filter */}
        <div className="filter-item">
          <MultiSelectDropdown
            label="Category"
            options={categories}
            selected={selectedCategories}
            onChange={setSelectedCategories}
            placeholder="Select categories..."
          />
        </div>

        {/* Organization Filter */}
        <div className="filter-item">
          <MultiSelectDropdown
            label="Organization"
            options={organizations.map(org => org.org_name)}
            selected={selectedOrganizations.map(org => org.org_name)}
            onChange={(selectedNames) => {
              const selectedOrgs = organizations.filter(org =>
                selectedNames.includes(org.org_name)
              )
              setSelectedOrganizations(selectedOrgs)
            }}
            placeholder="Select organizations..."
          />
        </div>

        {/* Event Type Filter */}
        <div className="filter-item">
          <label htmlFor="event-type">Event Type</label>
          <select
            id="event-type"
            value={selectedEventType}
            onChange={(e) => setSelectedEventType(e.target.value)}
            className="event-type-select"
          >
            <option value="">All Types</option>
            <option value="in_person">In Person</option>
            <option value="online">Online</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>

        {/* Date Range Filters */}
        <div className="filter-item">
          <label htmlFor="start-date">Start Date</label>
          <input
            id="start-date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="date-input"
          />
        </div>

        <div className="filter-item">
          <label htmlFor="end-date">End Date</label>
          <input
            id="end-date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="date-input"
          />
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="active-filters">
          <span className="active-filters-label">Active Filters:</span>
          {searchTerm && (
            <span className="filter-tag">
              Search: "{searchTerm}"
              <button onClick={() => setSearchTerm('')}>×</button>
            </span>
          )}
          {selectedCategories.map(cat => (
            <span key={cat} className="filter-tag">
              {cat}
              <button onClick={() => setSelectedCategories(selectedCategories.filter(c => c !== cat))}>×</button>
            </span>
          ))}
          {selectedOrganizations.map(org => (
            <span key={org.org_id} className="filter-tag">
              {org.org_name}
              <button onClick={() => setSelectedOrganizations(selectedOrganizations.filter(o => o.org_id !== org.org_id))}>×</button>
            </span>
          ))}
          {selectedEventType && (
            <span className="filter-tag">
              {selectedEventType.replace('_', ' ')}
              <button onClick={() => setSelectedEventType('')}>×</button>
            </span>
          )}
          {startDate && (
            <span className="filter-tag">
              From: {new Date(startDate).toLocaleDateString()}
              <button onClick={() => setStartDate('')}>×</button>
            </span>
          )}
          {endDate && (
            <span className="filter-tag">
              To: {new Date(endDate).toLocaleDateString()}
              <button onClick={() => setEndDate('')}>×</button>
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default FilterBar
