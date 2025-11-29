import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


def get_database_url():
    return os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/asu_events')


@contextmanager
def get_db_connection():
    '''
    Context manager for database connections.
    Automatically handles connection cleanup.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events")
            results = cursor.fetchall()

    Yields:
        psycopg2.connection: Database connection object
    '''
    conn = None
    try:
        conn = psycopg2.connect(get_database_url())
        yield conn
    except psycopg2.Error as e:
        print(f'Database connection error: {e}')
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    '''
    Context manager for database cursors.
    Returns results as dictionaries by default.

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM events")
            results = cursor.fetchall()  # Returns list of dicts

    Args:
        cursor_factory: Cursor factory class (default: RealDictCursor for dict results)

    Yields:
        psycopg2.cursor: Database cursor object
    '''
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


def get_events_paginated(page=1, limit=20, category=None, search=None):
    '''
    Get paginated events from the database.

    Args:
        page (int): Page number (1-indexed)
        limit (int): Number of events per page
        category (str): Optional category filter
        search (str): Optional search term for event names

    Returns:
        dict: Dictionary containing:
            - events: List of event dictionaries
            - pagination: Pagination metadata
    '''
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    offset = (page - 1) * limit

    where_clauses = []
    params = []

    if category:
        where_clauses.append('category = %s')
        params.append(category)

    if search:
        where_clauses.append('event_name ILIKE %s')
        params.append(f'%{search}%')

    where_sql = ''
    if where_clauses:
        where_sql = 'WHERE ' + ' AND '.join(where_clauses)

    count_query = f'SELECT COUNT(*) as total FROM events {where_sql}'

    events_query = f'''
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
            o.org_name
        FROM events e
        LEFT JOIN organizations o ON e.org_id = o.org_id
        {where_sql}
        ORDER BY e.event_start_datetime DESC NULLS LAST, e.event_id
        LIMIT %s OFFSET %s
    '''

    with get_db_cursor() as cursor:
        cursor.execute(count_query, params)
        total_events = cursor.fetchone()['total']

        cursor.execute(events_query, params + [limit, offset])
        events = cursor.fetchall()

        events = [dict(event) for event in events]

    total_pages = (total_events + limit - 1) // limit if total_events > 0 else 0

    return {
        'events': events,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_events': total_events,
            'limit': limit,
            'has_more': (page * limit) < total_events
        }
    }


def get_event_by_id(event_id):
    '''
    Get a single event by its ID.

    Args:
        event_id (str): Event ID

    Returns:
        dict: Event dictionary or None if not found
    '''
    query = '''
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
            o.org_name
        FROM events e
        LEFT JOIN organizations o ON e.org_id = o.org_id
        WHERE e.event_id = %s
    '''

    with get_db_cursor() as cursor:
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        return dict(event) if event else None


def get_categories():
    '''
    Get all unique event categories.

    Returns:
        list: List of category names
    '''
    query = '''
        SELECT DISTINCT category
        FROM events
        WHERE category IS NOT NULL
        ORDER BY category
    '''

    with get_db_cursor() as cursor:
        cursor.execute(query)
        categories = cursor.fetchall()
        return [cat['category'] for cat in categories]


def get_database_stats():
    '''
    Get database statistics.

    Returns:
        dict: Statistics including counts of events, organizations, categories, and event types
    '''
    with get_db_cursor() as cursor:
        cursor.execute('SELECT COUNT(*) as count FROM events')
        event_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM organizations')
        org_count = cursor.fetchone()['count']

        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM events
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        ''')
        categories = cursor.fetchall()

        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE event_type IS NOT NULL
            GROUP BY event_type
            ORDER BY count DESC
        ''')
        event_types = cursor.fetchall()

    return {
        'total_events': event_count,
        'total_organizations': org_count,
        'categories': [dict(cat) for cat in categories],
        'event_types': [dict(et) for et in event_types]
    }


def check_database_connection():
    '''
    Check if database connection is working.

    Returns:
        bool: True if connection successful, False otherwise
    '''
    try:
        with get_db_cursor() as cursor:
            cursor.execute('SELECT 1')
            return True
    except Exception as e:
        print(f'Database connection check failed: {e}')
        return False
