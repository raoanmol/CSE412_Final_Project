import { useState, useEffect, useRef, useCallback } from 'react'
import EventCard from './EventCard'
import api from '../services/api'
import './EventList.css'

function EventList() {
  const [events, setEvents] = useState([])
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [error, setError] = useState(null)
  const [totalEvents, setTotalEvents] = useState(0)

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

  const fetchEvents = async (pageNum) => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.get('/events', {
        params: {
          page: pageNum,
          limit: 20,
        },
      })

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

  useEffect(() => {
    fetchEvents(page)
  }, [page])

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
