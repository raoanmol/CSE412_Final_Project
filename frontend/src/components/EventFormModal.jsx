import { useState, useEffect } from 'react'
import api from '../services/api'
import './EventFormModal.css'

function EventFormModal({ event, orgId, categories, onClose, onSave }) {
  const [formData, setFormData] = useState({
    event_name: '',
    event_description: '',
    event_start_datetime: '',
    event_end_datetime: '',
    category: '',
    location_text: '',
    online_link: '',
    event_type: 'in_person',
    attendees: 0,
    picture_url: 'https://cdn.shopify.com/s/files/1/1095/6418/files/ASU-sun-devils-new-logo.jpg?v=1481918145',
    price_range: 'FREE'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showConfirmation, setShowConfirmation] = useState(false)

  const isEditMode = !!event

  useEffect(() => {
    if (event) {
      // Convert datetime strings to datetime-local format
      const formatDatetime = (dt) => {
        if (!dt) return ''
        const date = new Date(dt)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${year}-${month}-${day}T${hours}:${minutes}`
      }

      setFormData({
        event_name: event.event_name || '',
        event_description: event.event_description || '',
        event_start_datetime: formatDatetime(event.event_start_datetime),
        event_end_datetime: formatDatetime(event.event_end_datetime),
        category: event.category || '',
        location_text: event.location_text || '',
        online_link: event.online_link || '',
        event_type: event.event_type || 'in_person',
        attendees: event.attendees || 0,
        picture_url: event.picture_url || 'https://cdn.shopify.com/s/files/1/1095/6418/files/ASU-sun-devils-new-logo.jpg?v=1481918145',
        price_range: event.price_range || 'FREE'
      })
    }
  }, [event])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (isEditMode) {
      setShowConfirmation(true)
    } else {
      await saveEvent()
    }
  }

  const saveEvent = async () => {
    setLoading(true)
    setError(null)

    try {
      const dataToSend = {
        ...formData,
        org_id: orgId,
        // Convert datetime-local to ISO format
        event_start_datetime: formData.event_start_datetime ? new Date(formData.event_start_datetime).toISOString() : null,
        event_end_datetime: formData.event_end_datetime ? new Date(formData.event_end_datetime).toISOString() : null
      }

      let response
      if (isEditMode) {
        response = await api.put(`/events/${event.event_id}`, dataToSend)
      } else {
        response = await api.post('/events', dataToSend)
      }

      onSave(response.data, isEditMode ? 'update' : 'create')
      onClose()
    } catch (err) {
      console.error('Error saving event:', err)
      setError(err.response?.data?.message || 'Failed to save event')
      setLoading(false)
    }
  }

  const handleConfirmUpdate = () => {
    setShowConfirmation(false)
    saveEvent()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditMode ? 'Edit Event' : 'Add New Event'}</h2>
          <button onClick={onClose} className="close-btn">&times;</button>
        </div>

        {error && (
          <div className="error-message">{error}</div>
        )}

        {showConfirmation ? (
          <div className="confirmation-dialog">
            <p>Are you sure you want to update this event?</p>
            <div className="confirmation-actions">
              <button onClick={handleConfirmUpdate} className="confirm-btn" disabled={loading}>
                {loading ? 'Updating...' : 'Confirm Update'}
              </button>
              <button onClick={() => setShowConfirmation(false)} className="cancel-btn" disabled={loading}>
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="event-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="event_name">Event Name *</label>
                <input
                  type="text"
                  id="event_name"
                  name="event_name"
                  value={formData.event_name}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="category">Category *</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select a category</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="event_type">Event Type *</label>
                <select
                  id="event_type"
                  name="event_type"
                  value={formData.event_type}
                  onChange={handleChange}
                  required
                >
                  <option value="in_person">In Person</option>
                  <option value="online">Online</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="event_start_datetime">Start Date & Time</label>
                <input
                  type="datetime-local"
                  id="event_start_datetime"
                  name="event_start_datetime"
                  value={formData.event_start_datetime}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="event_end_datetime">End Date & Time</label>
                <input
                  type="datetime-local"
                  id="event_end_datetime"
                  name="event_end_datetime"
                  value={formData.event_end_datetime}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="location_text">Location</label>
                <input
                  type="text"
                  id="location_text"
                  name="location_text"
                  value={formData.location_text}
                  onChange={handleChange}
                  placeholder="e.g., Memorial Union, Room 101"
                />
              </div>

              <div className="form-group">
                <label htmlFor="online_link">Online Link</label>
                <input
                  type="text"
                  id="online_link"
                  name="online_link"
                  value={formData.online_link}
                  onChange={handleChange}
                  placeholder="https://... (optional)"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="price_range">Price</label>
                <input
                  type="text"
                  id="price_range"
                  name="price_range"
                  value={formData.price_range}
                  onChange={handleChange}
                  placeholder="e.g., FREE, $5-$10"
                />
              </div>

              <div className="form-group">
                <label htmlFor="attendees">Expected Attendees</label>
                <input
                  type="number"
                  id="attendees"
                  name="attendees"
                  value={formData.attendees}
                  onChange={handleChange}
                  min="0"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="event_description">Description</label>
                <textarea
                  id="event_description"
                  name="event_description"
                  value={formData.event_description}
                  onChange={handleChange}
                  rows="4"
                  placeholder="Event description..."
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="picture_url">Picture URL (optional)</label>
                <input
                  type="text"
                  id="picture_url"
                  name="picture_url"
                  value={formData.picture_url}
                  onChange={handleChange}
                  placeholder="https://... (leave default if unsure)"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? 'Saving...' : isEditMode ? 'Update Event' : 'Create Event'}
              </button>
              <button type="button" onClick={onClose} className="cancel-btn" disabled={loading}>
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default EventFormModal
