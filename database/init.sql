-- Database initialization script for ASU Events
-- This script creates the schema for storing events and clubs

-- Create clubs table
CREATE TABLE IF NOT EXISTS clubs (
    club_id VARCHAR(50) PRIMARY KEY,
    club_login VARCHAR(255),
    club_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(50) PRIMARY KEY,
    event_uid VARCHAR(255) UNIQUE,
    name VARCHAR(500) NOT NULL,
    dates TEXT,
    category VARCHAR(100),
    location TEXT,
    club_id VARCHAR(50),
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
    FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_events_club_id ON events(club_id);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);
CREATE INDEX IF NOT EXISTS idx_events_dates ON events(dates);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_clubs_updated_at BEFORE UPDATE ON clubs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for events with full club information
CREATE OR REPLACE VIEW events_with_clubs AS
SELECT
    e.event_id,
    e.event_uid,
    e.name,
    e.dates,
    e.category,
    e.location,
    e.attendees,
    e.picture_url,
    e.price_range,
    e.button_label,
    e.badges,
    e.event_url,
    e.timezone,
    e.aria_details,
    c.club_id,
    c.club_login,
    c.club_name,
    e.created_at,
    e.updated_at
FROM events e
LEFT JOIN clubs c ON e.club_id = c.club_id;

-- Output success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema initialized successfully!';
    RAISE NOTICE 'Created tables: clubs, events';
    RAISE NOTICE 'Created indexes for performance optimization';
    RAISE NOTICE 'Created view: events_with_clubs';
END $$;
