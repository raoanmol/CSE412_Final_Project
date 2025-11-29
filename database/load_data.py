import json
import os
import sys
import re
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from html import unescape


def get_db_connection():
    '''
    Create a connection to the PostgreSQL database.

    Returns:
        psycopg2.connection: Database connection object
    '''
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/asu_events')

    try:
        conn = psycopg2.connect(database_url)
        print('✓ Successfully connected to database')
        return conn
    except Exception as e:
        print(f'✗ Error connecting to database: {e}')
        sys.exit(1)


def load_json_data(json_file_path):
    '''
    Load events data from JSON file.

    Args:
        json_file_path (str): Path to the JSON file

    Returns:
        list: List of event dictionaries
    '''
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f'✓ Loaded {len(data)} events from {json_file_path}')
        return data
    except Exception as e:
        print(f'✗ Error loading JSON file: {e}')
        sys.exit(1)


def parse_datetime(date_string):
    '''
    Parse datetime from HTML date string.

    Args:
        date_string (str): HTML formatted date string like:
            "<p style='margin:0;'>Mon, Nov 3, 2025</p><p style='margin:0;'>5:30 PM – 7:30 PM</p>"

    Returns:
        tuple: (start_datetime, end_datetime, original_string) where datetimes are datetime objects or None
    '''
    if not date_string:
        return None, None, None

    original = date_string

    text = re.sub(r'<[^>]+>', ' ', date_string)
    text = unescape(text)
    text = ' '.join(text.split())

    start_dt = None
    end_dt = None

    try:
        # Pattern 1: "Day, Month Date, Year Time – Time"
        # Example: "Mon, Nov 3, 2025 5:30 PM – 7:30 PM"
        pattern1 = r'([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s+(\d+:\d+\s+[AP]M)\s+[-–—]\s+(\d+:\d+\s+[AP]M)'
        match = re.search(pattern1, text)

        if match:
            date_part = match.group(1)
            start_time = match.group(2)
            end_time = match.group(3)

            start_str = f"{date_part} {start_time}"
            start_dt = datetime.strptime(start_str, "%a, %b %d, %Y %I:%M %p")

            end_str = f"{date_part} {end_time}"
            end_dt = datetime.strptime(end_str, "%a, %b %d, %Y %I:%M %p")
        else:
            # Pattern 2: Date ranges across multiple days
            # Example: "Thu, Sep 4, 2025 1:00 PM – Thu, Dec 4, 2025 2:30 PM"
            pattern2 = r'([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s+(\d+:\d+\s+[AP]M)\s+[-–—]\s+([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s+(\d+:\d+\s+[AP]M)'
            match2 = re.search(pattern2, text)

            if match2:
                start_date = match2.group(1)
                start_time = match2.group(2)
                end_date = match2.group(3)
                end_time = match2.group(4)

                start_str = f"{start_date} {start_time}"
                start_dt = datetime.strptime(start_str, "%a, %b %d, %Y %I:%M %p")

                end_str = f"{end_date} {end_time}"
                end_dt = datetime.strptime(end_str, "%a, %b %d, %Y %I:%M %p")
            else:
                # Pattern 3: Just date and start time, no end time
                pattern3 = r'([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s+(\d+:\d+\s+[AP]M)'
                match3 = re.search(pattern3, text)

                if match3:
                    date_part = match3.group(1)
                    start_time = match3.group(2)
                    start_str = f"{date_part} {start_time}"
                    start_dt = datetime.strptime(start_str, "%a, %b %d, %Y %I:%M %p")

    except Exception as e:
        # If parsing fails, return None but keep original string
        print(f"⚠ Warning: Could not parse datetime: {text[:100]}... Error: {e}")

    return start_dt, end_dt, original


def parse_location(location_string):
    '''
    Parse location and extract online link if present.

    Args:
        location_string (str): Location string, may contain HTML with zoom links like:
            "GWC 487<div...><a href=\"https://asu.zoom.us/j/9306958576\">Zoom link</a></div>"

    Returns:
        tuple: (location_text, online_link, event_type)
            - location_text: Clean location text
            - online_link: URL if found, else None
            - event_type: 'in_person', 'online', or 'hybrid'
    '''
    if not location_string:
        return None, None, 'in_person'

    original = location_string

    # Extract URLs from href attributes
    url_pattern = r'href=["\']([^"\']+)["\']'
    urls = re.findall(url_pattern, location_string)
    online_link = urls[0] if urls else None

    # Remove HTML tags
    location_text = re.sub(r'<[^>]+>', ' ', location_string)
    location_text = unescape(location_text)
    location_text = ' '.join(location_text.split()).strip()

    # Remove text artifacts
    location_text = re.sub(r'\s*zoom\s+link\s*', '', location_text, flags=re.IGNORECASE)
    location_text = location_text.strip()

    # Determine event type
    has_physical_location = location_text and location_text.lower() not in ['online', 'online event', 'tbd', '']
    has_online_link = online_link is not None

    if has_physical_location and has_online_link:
        event_type = 'hybrid'
    elif has_online_link or (location_text and 'online' in location_text.lower()):
        event_type = 'online'
        if not has_online_link and location_text.lower() in ['online', 'online event']:
            location_text = 'Online'
    else:
        event_type = 'in_person'

    # Clean up empty location
    if not location_text or location_text.lower() == 'online event':
        location_text = 'Online' if event_type == 'online' else None

    return location_text, online_link, event_type


def extract_organizations(events):
    '''
    Extract unique organizations from events data.

    Args:
        events (list): List of event dictionaries

    Returns:
        list: List of unique organization dictionaries
    '''
    orgs_dict = {}

    for event in events:
        club_id = event.get('club_id')
        if club_id and club_id not in orgs_dict:
            orgs_dict[club_id] = {
                'org_id': club_id,
                'org_login': event.get('club_login'),
                'org_name': event.get('club_name')
            }

    return list(orgs_dict.values())


def insert_organizations(conn, organizations):
    '''
    Insert organizations into the database.

    Args:
        conn: Database connection
        organizations (list): List of organization dictionaries

    Returns:
        int: Number of organizations inserted
    '''
    if not organizations:
        print('No organizations to insert')
        return 0

    cursor = conn.cursor()

    org_values = [
        (org['org_id'], org['org_login'], org['org_name'])
        for org in organizations
    ]

    insert_query = '''
        INSERT INTO organizations (org_id, org_login, org_name)
        VALUES %s
        ON CONFLICT (org_id) DO UPDATE SET
            org_login = EXCLUDED.org_login,
            org_name = EXCLUDED.org_name,
            updated_at = CURRENT_TIMESTAMP
    '''

    try:
        execute_values(cursor, insert_query, org_values)
        conn.commit()
        print(f'✓ Inserted/updated {len(organizations)} organizations')
        return len(organizations)
    except Exception as e:
        conn.rollback()
        print(f'✗ Error inserting organizations: {e}')
        return 0
    finally:
        cursor.close()


def insert_events(conn, events):
    '''
    Insert events into the database with parsed datetime and location.

    Args:
        conn: Database connection
        events (list): List of event dictionaries

    Returns:
        int: Number of events inserted
    '''
    if not events:
        print('No events to insert')
        return 0

    cursor = conn.cursor()

    seen_ids = set()
    unique_events = []
    duplicates = 0
    parse_warnings = 0

    for event in events:
        event_id = event.get('event_id')
        if event_id and event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)
        else:
            duplicates += 1

    if duplicates > 0:
        print(f'⚠ Removed {duplicates} duplicate events from batch')

    event_values = []
    for event in unique_events:
        # Parse datetime
        start_dt, end_dt, original_date = parse_datetime(event.get('dates'))

        # Parse location
        location_text, online_link, event_type = parse_location(event.get('location'))

        event_values.append((
            event.get('event_id'),
            event.get('event_uid'),
            event.get('name'),
            event.get('description'),  # May be None in current data
            start_dt,
            end_dt,
            original_date,
            event.get('category'),
            location_text,
            online_link,
            event_type,
            event.get('club_id'),  # Will map to org_id in DB
            int(event.get('attendees', 0)) if event.get('attendees') and str(event.get('attendees')).isdigit() else 0,
            event.get('picture_url'),
            event.get('price_range'),
            event.get('button_label'),
            event.get('badges'),
            event.get('event_url'),
            event.get('timezone'),
            event.get('aria_details')
        ))

    insert_query = '''
        INSERT INTO events (
            event_id, event_uid, event_name, event_description,
            event_start_datetime, event_end_datetime, original_date_string,
            category, location_text, online_link, event_type, org_id,
            attendees, picture_url, price_range, button_label, badges,
            event_url, timezone, aria_details
        )
        VALUES %s
        ON CONFLICT (event_id) DO UPDATE SET
            event_uid = EXCLUDED.event_uid,
            event_name = EXCLUDED.event_name,
            event_description = EXCLUDED.event_description,
            event_start_datetime = EXCLUDED.event_start_datetime,
            event_end_datetime = EXCLUDED.event_end_datetime,
            original_date_string = EXCLUDED.original_date_string,
            category = EXCLUDED.category,
            location_text = EXCLUDED.location_text,
            online_link = EXCLUDED.online_link,
            event_type = EXCLUDED.event_type,
            org_id = EXCLUDED.org_id,
            attendees = EXCLUDED.attendees,
            picture_url = EXCLUDED.picture_url,
            price_range = EXCLUDED.price_range,
            button_label = EXCLUDED.button_label,
            badges = EXCLUDED.badges,
            event_url = EXCLUDED.event_url,
            timezone = EXCLUDED.timezone,
            aria_details = EXCLUDED.aria_details,
            updated_at = CURRENT_TIMESTAMP
    '''

    try:
        execute_values(cursor, insert_query, event_values)
        conn.commit()
        print(f'✓ Inserted/updated {len(unique_events)} events')
        return len(unique_events)
    except Exception as e:
        conn.rollback()
        print(f'✗ Error inserting events: {e}')
        return 0
    finally:
        cursor.close()


def get_database_stats(conn):
    '''
    Get statistics about the data in the database.

    Args:
        conn: Database connection

    Returns:
        dict: Dictionary with database statistics
    '''
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM organizations')
    stats['organizations'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM events')
    stats['events'] = cursor.fetchone()[0]

    cursor.execute('''
        SELECT category, COUNT(*)
        FROM events
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY COUNT(*) DESC
    ''')
    stats['categories'] = cursor.fetchall()

    cursor.execute('''
        SELECT event_type, COUNT(*)
        FROM events
        WHERE event_type IS NOT NULL
        GROUP BY event_type
        ORDER BY COUNT(*) DESC
    ''')
    stats['event_types'] = cursor.fetchall()

    cursor.close()
    return stats


def main():
    '''Main function to load data into database.'''

    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    else:
        docker_path = '/data/scraped_events.json'
        if os.path.exists(docker_path):
            json_file_path = docker_path
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            json_file_path = os.path.join(project_root, 'data', 'scraped_events.json')

    if not os.path.exists(json_file_path):
        print(f'✗ Error: JSON file not found at {json_file_path}')
        print('\nPlease run the scraper first:')
        print('  python utils/scraper.py')
        sys.exit(1)

    print('\nLoading ASU Events data into PostgreSQL...')
    print('='*60)

    events = load_json_data(json_file_path)

    conn = get_db_connection()

    try:
        organizations = extract_organizations(events)
        orgs_inserted = insert_organizations(conn, organizations)

        events_inserted = insert_events(conn, events)

        print('\n' + '='*60)
        print('DATABASE STATISTICS:')
        stats = get_database_stats(conn)
        print(f'  Total organizations: {stats["organizations"]}')
        print(f'  Total events: {stats["events"]}')

        if stats['categories']:
            print('\n  Events by category:')
            for category, count in stats['categories'][:10]:
                print(f'    {category}: {count}')

        if stats.get('event_types'):
            print('\n  Events by type:')
            for event_type, count in stats['event_types']:
                print(f'    {event_type}: {count}')

        print('\n✓ Data loading complete!')

    finally:
        conn.close()


if __name__ == '__main__':
    main()
