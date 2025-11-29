-- Database initialization script for ASU Events
-- This script creates the schema for storing events and organizations

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
    org_id VARCHAR(50) PRIMARY KEY,
    org_login VARCHAR(255),
    org_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(50) PRIMARY KEY,
    event_uid VARCHAR(255) UNIQUE,
    event_name VARCHAR(500) NOT NULL,
    event_description TEXT,
    event_start_datetime TIMESTAMP,
    event_end_datetime TIMESTAMP,
    original_date_string TEXT,
    category VARCHAR(100),
    location_text VARCHAR(500),
    online_link TEXT,
    event_type VARCHAR(20) CHECK (event_type IN ('in_person', 'online', 'hybrid')),
    org_id VARCHAR(50),
    attendees INTEGER DEFAULT 0,
    picture_url TEXT,
    price_range VARCHAR(100),
    button_label VARCHAR(100),
    badges TEXT,
    event_url TEXT,
    timezone VARCHAR(100),
    aria_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_events_org_id ON events(org_id);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(event_name);
CREATE INDEX IF NOT EXISTS idx_events_start_datetime ON events(event_start_datetime);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(10) PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    major VARCHAR(100),
    year INTEGER CHECK (year >= 1 AND year <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create student_organizations junction table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS student_organizations (
    student_id VARCHAR(10),
    org_id VARCHAR(50),
    join_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, org_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

-- Create student_officers table
CREATE TABLE IF NOT EXISTS student_officers (
    student_id VARCHAR(10),
    org_id VARCHAR(50),
    officer_title VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, org_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
    -- Note: Officers must be members constraint is enforced in application logic
);

-- Create indexes for students tables
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_students_major ON students(major);
CREATE INDEX IF NOT EXISTS idx_student_orgs_student_id ON student_organizations(student_id);
CREATE INDEX IF NOT EXISTS idx_student_orgs_org_id ON student_organizations(org_id);
CREATE INDEX IF NOT EXISTS idx_student_officers_student_id ON student_officers(student_id);
CREATE INDEX IF NOT EXISTS idx_student_officers_org_id ON student_officers(org_id);

-- Create a view for events with full organization information
CREATE OR REPLACE VIEW events_with_organizations AS
SELECT
    e.event_id,
    e.event_uid,
    e.event_name,
    e.event_description,
    e.event_start_datetime,
    e.event_end_datetime,
    e.original_date_string,
    e.category,
    e.location_text,
    e.online_link,
    e.event_type,
    e.attendees,
    e.picture_url,
    e.price_range,
    e.button_label,
    e.badges,
    e.event_url,
    e.timezone,
    e.aria_details,
    o.org_id,
    o.org_login,
    o.org_name,
    e.created_at,
    e.updated_at
FROM events e
LEFT JOIN organizations o ON e.org_id = o.org_id;

-- Output success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema initialized successfully!';
    RAISE NOTICE 'Created tables: organizations, events, students, student_organizations, student_officers';
    RAISE NOTICE 'Created indexes for performance optimization';
    RAISE NOTICE 'Created view: events_with_organizations';
END $$;
