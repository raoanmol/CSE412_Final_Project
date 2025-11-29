import './EventCard.css'

function EventCard({ event }) {
  // Format datetime for display
  const formatDateTime = (startDatetime, endDatetime, originalDateString) => {
    if (startDatetime) {
      const start = new Date(startDatetime)
      const options = {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      }
      let formatted = start.toLocaleDateString('en-US', options)

      if (endDatetime) {
        const end = new Date(endDatetime)
        const timeOptions = { hour: 'numeric', minute: '2-digit' }
        formatted += ` – ${end.toLocaleTimeString('en-US', timeOptions)}`
      }

      return formatted
    }

    // Fallback to original date string if parsed datetime not available
    if (originalDateString) {
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = originalDateString
      return tempDiv.textContent || originalDateString
    }

    return 'undefined'
  }

  // Clean up badges HTML
  const getBadges = (badgesHtml) => {
    if (!badgesHtml) return null
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = badgesHtml
    return tempDiv.textContent || ''
  }

  const handleEventClick = () => {
    if (event.event_url) {
      window.open(event.event_url, '_blank', 'noopener,noreferrer')
    }
  }

  const handleZoomClick = (e, zoomLink) => {
    e.stopPropagation() // Prevent card click
    window.open(zoomLink, '_blank', 'noopener,noreferrer')
  }

  return (
    <div className="event-card" onClick={handleEventClick}>
      <div className="event-image">
        {event.picture_url && (
          <img
            src={`https://sundevilcentral.eoss.asu.edu${event.picture_url}`}
            alt={event.event_name || event.name}
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/300x200?text=Event+Image'
            }}
          />
        )}
        {event.badges && (
          <div className="event-badges">
            {getBadges(event.badges)}
          </div>
        )}
      </div>
      <div className="event-content">
        <h3 className="event-title">{event.event_name || event.name}</h3>
        <div className="event-meta">
          <div className="event-date">
            <span className="icon">📅</span>
            <span>
              {formatDateTime(
                event.event_start_datetime,
                event.event_end_datetime,
                event.original_date_string
              )}
            </span>
          </div>
          {(event.location_text || event.online_link) && (
            <div className="event-location">
              <span className="icon">📍</span>
              <span>{event.location_text || 'Online'}</span>
              {event.online_link && (
                <a
                  href={event.online_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="zoom-link"
                  onClick={(e) => handleZoomClick(e, event.online_link)}
                >
                  🔗 {event.event_type === 'hybrid' ? 'Zoom Link' : 'Join Online'}
                </a>
              )}
            </div>
          )}
          <div className="event-category">
            <span className="icon">🏷️</span>
            <span>{event.category}</span>
          </div>
        </div>
        <div className="event-club">
          <span className="icon">👥</span>
          <span>{event.org_name || event.club_name}</span>
        </div>
        <div className="event-footer">
          {event.price_range && (
            <span className="event-price">{event.price_range}</span>
          )}
          {event.attendees > 0 && (
            <span className="event-attendees">
              {event.attendees} attendees
            </span>
          )}
          {event.button_label && (
            <button className="event-action-btn">
              {event.button_label}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default EventCard
