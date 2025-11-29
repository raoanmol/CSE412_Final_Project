import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
import random

MAJORS = [
    'Computer Science',
    'Software Engineering',
    'Business Administration',
    'Engineering',
    'Biology',
    'Psychology',
    'Political Science',
    'Communications',
    'Marketing',
    'Finance',
    'Mechanical Engineering',
    'Electrical Engineering',
    'Data Science',
    'Nursing',
    'Education',
    'Chemistry',
    'Physics',
    'Mathematics',
    'English',
    'History',
    'Art',
    'Music',
    'Theatre',
    'Philosophy',
    'Economics',
    'Accounting',
    'Supply Chain Management',
    'Cybersecurity',
    'Information Technology',
    'Biomedical Engineering'
]

FIRST_NAMES = [
    'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella', 'William',
    'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia', 'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander',
    'Abigail', 'Michael', 'Emily', 'Daniel', 'Elizabeth', 'Matthew', 'Sofia', 'Jackson', 'Avery', 'Sebastian',
    'Ella', 'David', 'Scarlett', 'Joseph', 'Grace', 'Carter', 'Chloe', 'Owen', 'Victoria', 'Wyatt',
    'Riley', 'John', 'Aria', 'Jack', 'Lily', 'Luke', 'Aubrey', 'Jayden', 'Zoey', 'Dylan',
    'Penelope', 'Grayson', 'Layla', 'Levi', 'Nora', 'Isaac', 'Hannah', 'Gabriel', 'Lillian', 'Julian',
    'Addison', 'Mateo', 'Eleanor', 'Anthony', 'Natalie', 'Jaxon', 'Luna', 'Lincoln', 'Savannah', 'Joshua',
    'Brooklyn', 'Christopher', 'Leah', 'Andrew', 'Zoe', 'Theodore', 'Stella', 'Caleb', 'Hazel', 'Ryan',
    'Ellie', 'Asher', 'Paisley', 'Nathan', 'Audrey', 'Thomas', 'Skylar', 'Leo', 'Violet', 'Isaiah'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
    'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
    'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts',
    'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker', 'Cruz', 'Edwards', 'Collins', 'Reyes',
    'Stewart', 'Morris', 'Morales', 'Murphy', 'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper',
    'Peterson', 'Bailey', 'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson'
]

# Officer titles
OFFICER_TITLES = {
    'president': 1,
    'vice_president': 1,
    'treasurer': 1,
    'secretary': 1,
    'events_coordinator': 1,
    'officer': 'remaining'
}


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


def generate_email(first_name, last_name, student_id):
    '''
    Generate ASU email address.

    Args:
        first_name (str): Student's first name
        last_name (str): Student's last name
        student_id (str): Student ID (used for uniqueness)

    Returns:
        str: Email address in format firstname.lastname@asu.edu or with number for uniqueness
    '''
    # Use last 4 digits of student ID for uniqueness if needed
    base_email = f"{first_name.lower()}.{last_name.lower()}@asu.edu"

    # Add a number from student_id to ensure uniqueness
    unique_suffix = student_id[-2:]  # Last 2 digits
    email_with_num = f"{first_name.lower()}.{last_name.lower()}{unique_suffix}@asu.edu"

    return email_with_num


def generate_student_id():
    '''
    Generate a random ASU student ID (10 digits starting with 1).

    Returns:
        str: Student ID
    '''
    return '1' + ''.join([str(random.randint(0, 9)) for _ in range(9)])


def generate_students(count):
    '''
    Generate random student data.

    Args:
        count (int): Number of students to generate

    Returns:
        list: List of student tuples (student_id, name, email, major, year)
    '''
    students = []
    used_ids = set()
    used_emails = set()

    for i in range(count):
        while True:
            student_id = generate_student_id()
            if student_id not in used_ids:
                used_ids.add(student_id)
                break

        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"

        while True:
            email = generate_email(first_name, last_name, student_id)
            if email not in used_emails:
                used_emails.add(email)
                break
            student_id = generate_student_id()

        major = random.choice(MAJORS)
        year = random.randint(1, 5)

        students.append((student_id, full_name, email, major, year))

    return students


def get_organizations(conn):
    '''
    Get all organization IDs from the database.

    Args:
        conn: Database connection

    Returns:
        list: List of organization IDs
    '''
    cursor = conn.cursor()
    cursor.execute('SELECT org_id FROM organizations ORDER BY org_id')
    org_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return org_ids


def insert_students(conn, students):
    '''
    Insert students into the database.

    Args:
        conn: Database connection
        students (list): List of student tuples

    Returns:
        int: Number of students inserted
    '''
    if not students:
        print('No students to insert')
        return 0

    cursor = conn.cursor()

    insert_query = '''
        INSERT INTO students (student_id, student_name, email, major, year)
        VALUES %s
        ON CONFLICT (student_id) DO UPDATE SET
            student_name = EXCLUDED.student_name,
            email = EXCLUDED.email,
            major = EXCLUDED.major,
            year = EXCLUDED.year
    '''

    try:
        execute_values(cursor, insert_query, students)
        conn.commit()
        print(f'✓ Inserted/updated {len(students)} students')
        return len(students)
    except Exception as e:
        conn.rollback()
        print(f'✗ Error inserting students: {e}')
        raise
    finally:
        cursor.close()


def assign_students_to_organizations(conn, student_ids, org_ids):
    '''
    Randomly assign students to organizations as members.
    Each organization gets 200-1500 members.

    Args:
        conn: Database connection
        student_ids (list): List of student IDs
        org_ids (list): List of organization IDs

    Returns:
        dict: Mapping of org_id to list of member student_ids
    '''
    cursor = conn.cursor()
    memberships = []
    org_members = {org_id: [] for org_id in org_ids}

    # Assign students to organizations
    for org_id in org_ids:
        num_members = random.randint(200, 1500)

        num_members = min(num_members, len(student_ids))

        members = random.sample(student_ids, num_members)
        org_members[org_id] = members

        for student_id in members:
            days_ago = random.randint(0, 1460)
            join_date = datetime.now() - timedelta(days=days_ago)

            is_active = random.random() < 0.95

            memberships.append((student_id, org_id, join_date.date(), is_active))

    insert_query = '''
        INSERT INTO student_organizations (student_id, org_id, join_date, is_active)
        VALUES %s
        ON CONFLICT (student_id, org_id) DO UPDATE SET
            join_date = EXCLUDED.join_date,
            is_active = EXCLUDED.is_active
    '''

    try:
        execute_values(cursor, insert_query, memberships)
        conn.commit()
        print(f'✓ Created {len(memberships)} student-organization memberships')
    except Exception as e:
        conn.rollback()
        print(f'✗ Error creating memberships: {e}')
        raise
    finally:
        cursor.close()

    return org_members


def assign_officers(conn, org_members):
    '''
    Assign officers for each organization.
    - Each org has 6-15 officers
    - 1 president, 1 VP, 1 treasurer, 1 secretary, 1 events coordinator, rest are generic officers
    - Students can only be officers in max 3 organizations
    - Officers must be members

    Args:
        conn: Database connection
        org_members (dict): Mapping of org_id to list of member student_ids

    Returns:
        int: Number of officer positions created
    '''
    cursor = conn.cursor()
    officer_assignments = []
    student_officer_count = {}

    for org_id, members in org_members.items():
        if not members:
            continue

        num_officers = random.randint(6, 15)
        num_officers = min(num_officers, len(members))

        eligible_members = [m for m in members if student_officer_count.get(m, 0) < 3]

        if len(eligible_members) < num_officers:
            num_officers = len(eligible_members)

        if num_officers == 0:
            continue

        selected_officers = random.sample(eligible_members, num_officers)

        officer_idx = 0
        for title, count in OFFICER_TITLES.items():
            if count == 'remaining':
                for i in range(officer_idx, len(selected_officers)):
                    student_id = selected_officers[i]
                    officer_assignments.append((student_id, org_id, 'officer'))
                    student_officer_count[student_id] = student_officer_count.get(student_id, 0) + 1
            else:
                for _ in range(count):
                    if officer_idx < len(selected_officers):
                        student_id = selected_officers[officer_idx]
                        officer_assignments.append((student_id, org_id, title))
                        student_officer_count[student_id] = student_officer_count.get(student_id, 0) + 1
                        officer_idx += 1

    insert_query = '''
        INSERT INTO student_officers (student_id, org_id, officer_title)
        VALUES %s
        ON CONFLICT (student_id, org_id) DO UPDATE SET
            officer_title = EXCLUDED.officer_title
    '''

    try:
        execute_values(cursor, insert_query, officer_assignments)
        conn.commit()
        print(f'✓ Created {len(officer_assignments)} officer positions')

        students_with_multiple_positions = sum(1 for count in student_officer_count.values() if count > 1)
        students_with_max_positions = sum(1 for count in student_officer_count.values() if count == 3)
        print(f'  - {students_with_multiple_positions} students have multiple officer positions')
        print(f'  - {students_with_max_positions} students have the maximum (3) officer positions')

    except Exception as e:
        conn.rollback()
        print(f'✗ Error creating officer positions: {e}')
        raise
    finally:
        cursor.close()

    return len(officer_assignments)


def get_database_stats(conn):
    '''
    Get statistics about the student data in the database.

    Args:
        conn: Database connection

    Returns:
        dict: Dictionary with database statistics
    '''
    cursor = conn.cursor()
    stats = {}

    cursor.execute('SELECT COUNT(*) FROM students')
    stats['students'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM student_organizations')
    stats['memberships'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM student_officers')
    stats['officers'] = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(DISTINCT org_id)
        FROM student_organizations
    ''')
    stats['orgs_with_members'] = cursor.fetchone()[0]

    cursor.execute('''
        SELECT major, COUNT(*) as count
        FROM students
        WHERE major IS NOT NULL
        GROUP BY major
        ORDER BY count DESC
        LIMIT 5
    ''')
    stats['top_majors'] = cursor.fetchall()

    cursor.execute('''
        SELECT year, COUNT(*) as count
        FROM students
        GROUP BY year
        ORDER BY year
    ''')
    stats['students_by_year'] = cursor.fetchall()

    cursor.execute('''
        SELECT officer_title, COUNT(*) as count
        FROM student_officers
        GROUP BY officer_title
        ORDER BY count DESC
    ''')
    stats['officer_titles'] = cursor.fetchall()

    cursor.close()
    return stats


def main():
    '''Main function to generate and load student data.'''

    num_students = 5000
    if len(sys.argv) > 1:
        try:
            num_students = int(sys.argv[1])
        except ValueError:
            print(f'⚠ Invalid number of students, using default: {num_students}')

    print('\nGenerating student data for ASU Events database...')
    print('='*60)
    print(f'Generating {num_students} students...')

    conn = get_db_connection()

    try:
        org_ids = get_organizations(conn)
        if not org_ids:
            print('✗ Error: No organizations found in database')
            print('  Please run load_data.py first to populate organizations')
            sys.exit(1)

        print(f'✓ Found {len(org_ids)} organizations in database')

        students = generate_students(num_students)
        student_ids = [s[0] for s in students]

        insert_students(conn, students)

        org_members = assign_students_to_organizations(conn, student_ids, org_ids)

        assign_officers(conn, org_members)

        print('\n' + '='*60)
        print('DATABASE STATISTICS:')
        stats = get_database_stats(conn)
        print(f'  Total students: {stats["students"]}')
        print(f'  Total memberships: {stats["memberships"]}')
        print(f'  Total officer positions: {stats["officers"]}')
        print(f'  Organizations with members: {stats["orgs_with_members"]}')

        if stats['students_by_year']:
            print('\n  Students by year:')
            year_labels = {1: 'Freshman', 2: 'Sophomore', 3: 'Junior', 4: 'Senior', 5: 'Graduate'}
            for year, count in stats['students_by_year']:
                print(f'    {year_labels.get(year, f"Year {year}")}: {count}')

        if stats['top_majors']:
            print('\n  Top 5 majors:')
            for major, count in stats['top_majors']:
                print(f'    {major}: {count}')

        if stats['officer_titles']:
            print('\n  Officer positions by title:')
            for title, count in stats['officer_titles']:
                print(f'    {title.replace("_", " ").title()}: {count}')

        print('\n✓ Student data generation complete!')

    finally:
        conn.close()


if __name__ == '__main__':
    main()
