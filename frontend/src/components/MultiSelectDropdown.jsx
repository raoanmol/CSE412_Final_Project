import { useState, useRef, useEffect } from 'react'
import './MultiSelectDropdown.css'

function MultiSelectDropdown({ options, selected, onChange, placeholder, label }) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const dropdownRef = useRef(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const filteredOptions = options.filter((option) =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleToggle = (option) => {
    if (selected.includes(option)) {
      onChange(selected.filter((item) => item !== option))
    } else {
      onChange([...selected, option])
    }
  }

  const handleClearAll = () => {
    onChange([])
  }

  return (
    <div className="multi-select-dropdown" ref={dropdownRef}>
      {label && <label className="dropdown-label">{label}</label>}
      <button
        className="dropdown-toggle"
        onClick={() => setIsOpen(!isOpen)}
        type="button"
      >
        <span className="dropdown-text">
          {selected.length === 0
            ? placeholder
            : `${selected.length} selected`}
        </span>
        <span className="dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          <div className="dropdown-search">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
          </div>

          {selected.length > 0 && (
            <div className="dropdown-actions">
              <button
                className="clear-all-btn"
                onClick={handleClearAll}
                type="button"
              >
                Clear All ({selected.length})
              </button>
            </div>
          )}

          <div className="dropdown-options">
            {filteredOptions.length === 0 ? (
              <div className="no-options">No options found</div>
            ) : (
              filteredOptions.map((option) => (
                <label key={option} className="dropdown-option">
                  <input
                    type="checkbox"
                    checked={selected.includes(option)}
                    onChange={() => handleToggle(option)}
                  />
                  <span className="option-text">{option}</span>
                </label>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default MultiSelectDropdown
