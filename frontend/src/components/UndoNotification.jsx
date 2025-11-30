import { useEffect, useState } from 'react'
import './UndoNotification.css'

function UndoNotification({ message, onUndo, onComplete, duration = 5000 }) {
  const [timeLeft, setTimeLeft] = useState(duration)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 100) {
          clearInterval(interval)
          handleComplete()
          return 0
        }
        return prev - 100
      })
    }, 100)

    return () => clearInterval(interval)
  }, [])

  const handleComplete = () => {
    setIsVisible(false)
    setTimeout(() => {
      onComplete()
    }, 300) // Wait for fade out animation
  }

  const handleUndo = () => {
    setIsVisible(false)
    setTimeout(() => {
      onUndo()
    }, 300)
  }

  const progressPercent = (timeLeft / duration) * 100

  return (
    <div className={`undo-notification ${isVisible ? 'visible' : ''}`}>
      <div className="undo-content">
        <span className="undo-message">{message}</span>
        <button onClick={handleUndo} className="undo-btn">
          Undo
        </button>
      </div>
      <div className="undo-progress">
        <div
          className="undo-progress-bar"
          style={{ width: `${progressPercent}%` }}
        />
      </div>
    </div>
  )
}

export default UndoNotification
