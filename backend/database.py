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


def get_events_paginated(page=1, limit=20, category=None, search=None, event_type=None,
                         start_date=None, end_date=None, organization=None):
    '''
    Get paginated events from the database.

    Args:
        page (int): Page number (1-indexed)
        limit (int): Number of events per page
        category (str or list): Optional category filter(s)
        search (str): Optional search term for event names
        event_type (str): Optional event type filter (in_person, online, hybrid)
        start_date (str): Optional start date filter (ISO format)
        end_date (str): Optional end date filter (ISO format)
        organization (str or list): Optional organization filter(s)

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

    # Category filter
    if category:
        if isinstance(category, list):
            placeholders = ','.join(['%s'] * len(category))
            where_clauses.append(f'category IN ({placeholders})')
            params.extend(category)
        else:
            where_clauses.append('category = %s')
            params.append(category)

    # Text search
    if search:
        where_clauses.append('event_name ILIKE %s')
        params.append(f'%{search}%')

    # Event type filter
    if event_type:
        where_clauses.append('event_type = %s')
        params.append(event_type)

    # Date range filter
    if start_date:
        where_clauses.append('event_start_datetime >= %s')
        params.append(start_date)

    if end_date:
        where_clauses.append('event_start_datetime <= %s')
        params.append(end_date)

    # Organization filter
    if organization:
        if isinstance(organization, list):
            placeholders = ','.join(['%s'] * len(organization))
            where_clauses.append(f'e.org_id IN ({placeholders})')
            params.extend(organization)
        else:
            where_clauses.append('e.org_id = %s')
            params.append(organization)

    where_sql = ''
    if where_clauses:
        where_sql = 'WHERE ' + ' AND '.join(where_clauses)

    count_query = f'SELECT COUNT(*) as total FROM events e {where_sql}'

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


def get_organizations():
    '''
    Get all organizations.

    Returns:
        list: List of organization dictionaries
    '''
    query = '''
        SELECT org_id, org_login, org_name
        FROM organizations
        ORDER BY org_name
    '''

    with get_db_cursor() as cursor:
        cursor.execute(query)
        organizations = cursor.fetchall()
        return [dict(org) for org in organizations]


def get_organizations_with_stats(search=None, sort_by=None):
    '''
    Get organizations with their statistics (event count, member count, officer count).

    Args:
        search (str): Optional search term for organization name
        sort_by (str): Optional sort field ('events', 'members', 'officers', 'name')

    Returns:
        list: List of organization dictionaries with stats
    '''
    where_clause = ''
    params = []

    if search:
        where_clause = 'WHERE o.org_name ILIKE %s'
        params.append(f'%{search}%')

    # Determine sort order
    order_by = 'o.org_name'  # default
    if sort_by == 'events':
        order_by = 'event_count DESC NULLS LAST, o.org_name'
    elif sort_by == 'members':
        order_by = 'member_count DESC NULLS LAST, o.org_name'
    elif sort_by == 'officers':
        order_by = 'officer_count DESC NULLS LAST, o.org_name'

    query = f'''
        SELECT
            o.org_id,
            o.org_login,
            o.org_name,
            COUNT(DISTINCT e.event_id) as event_count,
            COUNT(DISTINCT so.student_id) as member_count,
            COUNT(DISTINCT sof.student_id) as officer_count
        FROM organizations o
        LEFT JOIN events e ON o.org_id = e.org_id
        LEFT JOIN student_organizations so ON o.org_id = so.org_id
        LEFT JOIN student_officers sof ON o.org_id = sof.org_id
        {where_clause}
        GROUP BY o.org_id, o.org_login, o.org_name
        ORDER BY {order_by}
    '''

    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        organizations = cursor.fetchall()
        return [dict(org) for org in organizations]


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
