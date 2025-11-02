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
