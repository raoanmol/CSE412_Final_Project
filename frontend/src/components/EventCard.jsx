import './EventCard.css'

function EventCard({ event }) {
  // Parse the HTML dates to extract readable text
  const parseDates = (datesHtml) => {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = datesHtml
    return tempDiv.textContent || datesHtml
  }

  // Clean up badges HTML
  const getBadges = (badgesHtml) => {
    if (!badgesHtml) return null
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = badgesHtml
    return tempDiv.textContent || ''
  }

  // Parse location and extract zoom link if present
  const parseLocation = (locationHtml) => {
    if (!locationHtml) return { text: '', zoomLink: null }

    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = locationHtml

    // Extract zoom link if present
    const link = tempDiv.querySelector('a[href*="zoom.us"]')
    const zoomLink = link ? link.href : null

    // Get the text content (location name)
    const locationText = tempDiv.textContent || locationHtml

    return { text: locationText.replace('Zoom link', '').trim(), zoomLink }
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

  const locationInfo = parseLocation(event.location)

  return (
    <div className="event-card" onClick={handleEventClick}>
      <div className="event-image">
        {event.picture_url && (
          <img
            src={`https://sundevilcentral.eoss.asu.edu${event.picture_url}`}
            alt={event.name}
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
        <h3 className="event-title">{event.name}</h3>
        <div className="event-meta">
          <div className="event-date">
            <span className="icon">📅</span>
            <span>{parseDates(event.dates)}</span>
          </div>
          {event.location && (
            <div className="event-location">
              <span className="icon">📍</span>
              <span>{locationInfo.text}</span>
              {locationInfo.zoomLink && (
                <a
                  href={locationInfo.zoomLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="zoom-link"
                  onClick={(e) => handleZoomClick(e, locationInfo.zoomLink)}
                >
                  🔗 Zoom Link
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
          <span>{event.club_name}</span>
        </div>
        <div className="event-footer">
          {event.price_range && (
            <span className="event-price">{event.price_range}</span>
          )}
          {event.attendees && (
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
