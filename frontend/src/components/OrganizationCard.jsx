import './OrganizationCard.css'

function OrganizationCard({ organization, onClick }) {
  const handleClick = () => {
    if (onClick) {
      onClick(organization.org_id)
    }
  }

  return (
    <div className="org-card" onClick={handleClick}>
      <div className="org-content">
        <h3 className="org-name">{organization.org_name}</h3>

        <div className="org-stats">
          <div className="org-stat">
            <span className="stat-icon">📅</span>
            <div className="stat-info">
              <span className="stat-value">{organization.event_count || 0}</span>
              <span className="stat-label">Events</span>
            </div>
          </div>

          <div className="org-stat">
            <span className="stat-icon">👥</span>
            <div className="stat-info">
              <span className="stat-value">{organization.member_count || 0}</span>
              <span className="stat-label">Members</span>
            </div>
          </div>

          <div className="org-stat">
            <span className="stat-icon">⭐</span>
            <div className="stat-info">
              <span className="stat-value">{organization.officer_count || 0}</span>
              <span className="stat-label">Officers</span>
            </div>
          </div>
        </div>

        {organization.org_login && (
          <div className="org-login">
            <span className="icon">🔗</span>
            <span className="login-text">{organization.org_login}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default OrganizationCard
