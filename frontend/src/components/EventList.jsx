import { useState, useEffect, useRef, useCallback } from 'react'
import EventCard from './EventCard'
import FilterBar from './FilterBar'
import api from '../services/api'
import './EventList.css'

function EventList() {
  const [events, setEvents] = useState([])
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [error, setError] = useState(null)
  const [totalEvents, setTotalEvents] = useState(0)
  const [filters, setFilters] = useState({})

  const observer = useRef()
  const lastEventElementRef = useCallback(
    (node) => {
      if (loading) return
      if (observer.current) observer.current.disconnect()

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          setPage((prevPage) => prevPage + 1)
        }
      })

      if (node) observer.current.observe(node)
    },
    [loading, hasMore]
  )

  const fetchEvents = async (pageNum, currentFilters) => {
    try {
      setLoading(true)
      setError(null)

      const params = {
        page: pageNum,
        limit: 20,
      }

      if (currentFilters.search) params.search = currentFilters.search
      if (currentFilters.category) params.category = currentFilters.category.join(',')
      if (currentFilters.organization) params.organization = currentFilters.organization.join(',')
      if (currentFilters.event_type) params.event_type = currentFilters.event_type
      if (currentFilters.start_date) params.start_date = currentFilters.start_date
      if (currentFilters.end_date) params.end_date = currentFilters.end_date

      const response = await api.get('/events', { params })

      const { events: newEvents, pagination } = response.data

      setEvents((prevEvents) => {
        // Avoid duplicates by checking event IDs
        const existingIds = new Set(prevEvents.map((e) => e.event_id))
        const uniqueNewEvents = newEvents.filter((e) => !existingIds.has(e.event_id))
        return [...prevEvents, ...uniqueNewEvents]
      })

      setHasMore(pagination.has_more)
      setTotalEvents(pagination.total_events)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching events:', err)
      setError('Failed to load events. Please try again.')
      setLoading(false)
    }
  }

  // Fetch events when page changes
  useEffect(() => {
    fetchEvents(page, filters)
  }, [page])

  // Reset and fetch when filters change
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters)
    setEvents([])
    setPage(1)
    setHasMore(true)
    fetchEvents(1, newFilters)
  }, [])

  const handleRetry = () => {
    setError(null)
    setPage(1)
    setEvents([])
    setHasMore(true)
  }

  if (error && events.length === 0) {
    return (
      <div className="event-list-error">
        <p>{error}</p>
        <button onClick={handleRetry} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="event-list-container">
      <div className="event-list-header">
        <h2>ASU Events</h2>
        <p className="event-count">
          Showing {events.length} of {totalEvents} events
        </p>
      </div>

      <FilterBar onFilterChange={handleFilterChange} />

      <div className="event-list">
        {events.map((event, index) => {
          if (events.length === index + 1) {
            return (
              <div ref={lastEventElementRef} key={event.event_uid || event.event_id}>
                <EventCard event={event} />
              </div>
            )
          } else {
            return (
              <div key={event.event_uid || event.event_id}>
                <EventCard event={event} />
              </div>
            )
          }
        })}
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading more events...</p>
        </div>
      )}

      {!hasMore && events.length > 0 && (
        <div className="end-message">
          <p>You've reached the end of the events list!</p>
        </div>
      )}

      {error && events.length > 0 && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => fetchEvents(page)} className="retry-btn">
            Retry
          </button>
        </div>
      )}
    </div>
  )
}

export default EventList
