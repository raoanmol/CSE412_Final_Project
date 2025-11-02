from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

dotenv_path = os.path.join(project_root, 'utils', '.env')
load_dotenv(dotenv_path)

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

conn = psycopg2.connect(database=DB_NAME, user=DB_USER,
                        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

cur = conn.cursor()

print("Database connection established")

create_student_table_query = """
    CREATE TABLE IF NOT EXISTS student (
        asuid INT PRIMARY KEY NOT NULL,
        name VARCHAR(50) NOT NULL,
        password VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
    );
"""
cur.execute(create_student_table_query)

# student interests list implemented as junction table
create_student_interests_table_query = """
    CREATE TABLE IF NOT EXISTS student_interests (
        asuid INT NOT NULL,
        interest VARCHAR(100) NOT NULL,
        PRIMARY KEY (asuid),
        FOREIGN KEY (asuid) REFERENCES student(asuid) ON DELETE CASCADE
    );
"""
cur.execute(create_student_interests_table_query)

create_organization_table_query = """
    CREATE TABLE IF NOT EXISTS organization (
        orgid SERIAL PRIMARY KEY NOT NULL,
        orgtype VARCHAR(50) NOT NULL,
        name VARCHAR(100) UNIQUE NOT NULL
    );
"""
cur.execute(create_organization_table_query)

# org officers list implemented as junction table
create_org_officers_table_query = """
    CREATE TABLE IF NOT EXISTS organization_officers (
        orgid INT NOT NULL,
        asuid INT NOT NULL,
        position VARCHAR(50),
        PRIMARY KEY (orgid, asuid),
        FOREIGN KEY (orgid) REFERENCES organization(orgid) ON DELETE CASCADE,
        FOREIGN KEY (asuid) REFERENCES student(asuid) ON DELETE CASCADE
    );
"""
cur.execute(create_org_officers_table_query)

# org members list implemented as junction table
create_org_members_table_query = """
    CREATE TABLE IF NOT EXISTS organization_members (
        orgid INT NOT NULL,
        asuid INT NOT NULL,
        join_date DATE DEFAULT CURRENT_DATE,
        PRIMARY KEY (orgid, asuid),
        FOREIGN KEY (orgid) REFERENCES organization(orgid) ON DELETE CASCADE,
        FOREIGN KEY (asuid) REFERENCES student(asuid) ON DELETE CASCADE
    );
"""
cur.execute(create_org_members_table_query)

create_event_table_query = """
    CREATE TABLE IF NOT EXISTS event (
        eventid INT PRIMARY KEY NOT NULL, 
        orgid INT NOT NULL,
        locationid INT NOT NULL,
        PRIMARY KEY (orgid, locationid),
        FOREGIN KEY (orgid) REFERENCES organization(orgid) ON DELETE CASCADE,
        FOREGIN KEY (locationid) REFERENCES location(locationid) ON DELETE CASCADE,
        date DATE NOT NULL,
        name varchar(100) NOT NULL,
        description VARCHAR(500)
    );
"""
cur.execute(create_event_table_query)

#attendence list implemented as junction table
create_event_attendance_table_query = """
    CREATE TABLE IF NOT EXISTS event_attendance (
        eventid INT NOT NULL,
        asuid INT NOT NULL,
        PRIMARY KEY (eventid, asuid),
        FOREIGN KEY (eventid) REFERENCES event(eventid) ON DELETE CASCADE,
        FOREIGN KEY (asuid) REFERENCES student(asuid) ON DELETE CASCADE
    );
"""
cur.execute(create_event_attendance_table_query)

create_location_table_query = """
    CREATE TABLE IF NOT EXISTS location (
        locationid INT PRIMARY KEY NOT NULL,
        campus VARCHAR(100) NOT NULL,
        building VARCHAR(100) NOT NULL,
        roomnumber VARCHAR(50) NOT NULL,
        isonline BOOLEAN DEFAULT FALSE
    );
"""
cur.execute(create_location_table_query)

cur.close()
conn.close()