import json
import os
import sys
import psycopg2
from psycopg2.extras import execute_values


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


def extract_clubs(events):
    '''
    Extract unique clubs from events data.

    Args:
        events (list): List of event dictionaries

    Returns:
        list: List of unique club dictionaries
    '''
    clubs_dict = {}

    for event in events:
        club_id = event.get('club_id')
        if club_id and club_id not in clubs_dict:
            clubs_dict[club_id] = {
                'club_id': club_id,
                'club_login': event.get('club_login'),
                'club_name': event.get('club_name')
            }

    return list(clubs_dict.values())


def insert_clubs(conn, clubs):
    '''
    Insert clubs into the database.

    Args:
        conn: Database connection
        clubs (list): List of club dictionaries

    Returns:
        int: Number of clubs inserted
    '''
    if not clubs:
        print('No clubs to insert')
        return 0

    cursor = conn.cursor()

    club_values = [
        (club['club_id'], club['club_login'], club['club_name'])
        for club in clubs
    ]

    insert_query = '''
        INSERT INTO clubs (club_id, club_login, club_name)
        VALUES %s
        ON CONFLICT (club_id) DO UPDATE SET
            club_login = EXCLUDED.club_login,
            club_name = EXCLUDED.club_name,
            updated_at = CURRENT_TIMESTAMP
    '''

    try:
        execute_values(cursor, insert_query, club_values)
        conn.commit()
        print(f'✓ Inserted/updated {len(clubs)} clubs')
        return len(clubs)
    except Exception as e:
        conn.rollback()
        print(f'✗ Error inserting clubs: {e}')
        return 0
    finally:
        cursor.close()


def insert_events(conn, events):
    '''
    Insert events into the database.

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

    for event in events:
        event_id = event.get('event_id')
        if event_id and event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)
        else:
            duplicates += 1

    if duplicates > 0:
        print(f'⚠ Removed {duplicates} duplicate events from batch')

    event_values = [
        (
            event.get('event_id'),
            event.get('event_uid'),
            event.get('name'),
            event.get('dates'),
            event.get('category'),
            event.get('location'),
            event.get('club_id'),
            int(event.get('attendees', 0)) if event.get('attendees') and str(event.get('attendees')).isdigit() else 0,
            event.get('picture_url'),
            event.get('price_range'),
            event.get('button_label'),
            event.get('badges'),
            event.get('event_url'),
            event.get('timezone'),
            event.get('aria_details')
        )
        for event in unique_events
    ]

    insert_query = '''
        INSERT INTO events (
            event_id, event_uid, name, dates, category, location, club_id,
            attendees, picture_url, price_range, button_label, badges,
            event_url, timezone, aria_details
        )
        VALUES %s
        ON CONFLICT (event_id) DO UPDATE SET
            event_uid = EXCLUDED.event_uid,
            name = EXCLUDED.name,
            dates = EXCLUDED.dates,
            category = EXCLUDED.category,
            location = EXCLUDED.location,
            club_id = EXCLUDED.club_id,
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
        print(f'✓ Inserted/updated {len(events)} events')
        return len(events)
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

    cursor.execute('SELECT COUNT(*) FROM clubs')
    stats['clubs'] = cursor.fetchone()[0]

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
        clubs = extract_clubs(events)
        clubs_inserted = insert_clubs(conn, clubs)

        events_inserted = insert_events(conn, events)

        print('\n' + '='*60)
        print('DATABASE STATISTICS:')
        stats = get_database_stats(conn)
        print(f'  Total clubs: {stats["clubs"]}')
        print(f'  Total events: {stats["events"]}')

        if stats['categories']:
            print('\n  Events by category:')
            for category, count in stats['categories'][:10]:
                print(f'    {category}: {count}')

        print('\n✓ Data loading complete!')

    finally:
        conn.close()


if __name__ == '__main__':
    main()
