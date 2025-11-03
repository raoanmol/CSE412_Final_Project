# CSE412 Final Project

A full-stack web application with a React frontend and Flask backend.

## Project Structure

```
.
├── backend/              # Flask backend server
|   ├── database.py      # SQL commads to query PostgreSQL database
│   ├── Dockerfile       # Backend container configuration
|   ├── main.py          # Main Flask application
│   └── startup.sh       # Backend startup script (populates database too)
├── frontend/             # React frontend application
│   ├── Dockerfile       # Frontend container configuration
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── services/
│   │   │   └── api.js   # Axios API client
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── database/             # Database scripts and schema
│   ├── init.sql         # PostgreSQL schema initialization
│   └── load_data.py     # Script to load JSON data into database
├── utils/                # Utility scripts
│   ├── scraper.py       # ASU Sun Devil Central Events Scraper
│   └── .env.example     # Scraper credentials template
├── docker-compose.yml    # Docker orchestration (includes PostgreSQL)
├── Makefile             # Simple commands for Docker
├── requirements.txt     # Python dependencies (consolidated)
├── .gitignore           # Git ignore rules (consolidated)
└── README.md            # This file
```

## Quick Start

### Option 1: Using Docker (Recommended)

**Prerequisites:** Make sure you have [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

1. Start the application:
   ```bash
   make up
   ```

That's it! The command will:
- Build Docker images for frontend, backend, and database
- Start all three containers
- Set up networking between them
- Initialize the PostgreSQL database with schema
- **Automatically load scraped data if database is empty**
- Frontend will be available at `http://localhost:3000`
- Backend will be available at `http://localhost:43798`
- Database will be available at `localhost:5433` (external port to avoid conflicts)

**Note:** The backend automatically checks if the database is empty on startup. If it is, it will load data from `data/scraped_events.json`. You can also manually reload data anytime with:
```bash
make db-load
```

**Other useful commands:**
```bash
make down            # Stop the application
make logs            # View logs from all containers
make logs-backend    # View only backend logs
make logs-frontend   # View only frontend logs
make logs-db         # View only database logs
make restart         # Restart the application
make build           # Rebuild containers (use after changing dependencies)
make clean           # Remove all containers and volumes
make db-connect      # Connect to database with psql
make db-reset        # Reset database (WARNING: deletes all data)
make help            # See all available commands
```

**How it works:**
- Docker creates isolated "containers" (like lightweight virtual machines) for your frontend, backend, and database
- Each container has its own environment with all dependencies installed
- The containers can talk to each other through a virtual network
- Your code is "mounted" into the containers, so changes you make are reflected immediately (hot-reload)
- The PostgreSQL database persists data in a Docker volume (survives container restarts)
- No need to install Python, Node, PostgreSQL, or any dependencies on your machine!

### Option 2: Manual Setup (Without Docker)

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies from the root directory:
   ```bash
   cd ..
   pip install -r requirements.txt
   ```

   Or install from within the backend directory:
   ```bash
   pip install -r ../requirements.txt
   ```

5. Run the backend server (make sure you're in the backend directory):
   ```bash
   cd backend  # If you went back to root in step 4
   python main.py
   ```

**Note:** When running manually (without Docker), the backend will start on `http://localhost:5000` by default. You'll need to update [backend/main.py:30](backend/main.py#L30) if you want to use port 43798.

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will start on `http://localhost:3000`

## Database

The application uses PostgreSQL to store events and clubs data.

### Database Schema

**Tables:**
- `clubs` - Student clubs and organizations
  - `club_id` (PRIMARY KEY)
  - `club_login`
  - `club_name`
  - `created_at`, `updated_at`

- `events` - Events hosted by clubs
  - `event_id` (PRIMARY KEY)
  - `event_uid` (UNIQUE)
  - `name`, `dates`, `category`, `location`
  - `club_id` (FOREIGN KEY → clubs)
  - `attendees`, `picture_url`, `price_range`
  - `button_label`, `badges`, `event_url`
  - `timezone`, `aria_details`
  - `created_at`, `updated_at`

**Views:**
- `events_with_clubs` - Joins events with their associated club information

### Database Commands

```bash
# Load scraped data into database
make db-load

# Connect to database with psql
make db-connect

# View database logs
make logs-db

# Reset database (deletes all data)
make db-reset
```

### Database Configuration

When running with Docker:
- **Host:** `localhost` (from your machine) or `db` (from backend container)
- **Port:** `5433` (external), `5432` (internal container port)
- **Database:** `asu_events`
- **User:** `postgres`
- **Password:** `postgres`
- **Connection String (from host):** `postgresql://postgres:postgres@localhost:5433/asu_events`
- **Connection String (from backend):** `postgresql://postgres:postgres@db:5432/asu_events`

**Note:** The database is exposed on port 5433 externally to avoid conflicts with any local PostgreSQL instance you might have running on port 5432. Inside the Docker network, containers communicate on the standard port 5432.

## API Endpoints

The backend provides the following REST API endpoints:

### Events
- `GET /api/events` - Get paginated events
  - Query parameters:
    - `page` (int, default: 1) - Page number
    - `limit` (int, default: 20, max: 100) - Events per page
    - `category` (string, optional) - Filter by category
    - `search` (string, optional) - Search in event names
  - Example: `/api/events?page=1&limit=20&category=Social&search=gaming`

- `GET /api/events/<event_id>` - Get a single event by ID
  - Returns 404 if event not found

### Categories
- `GET /api/categories` - Get all unique event categories
  - Returns list of categories and count

### Statistics
- `GET /api/stats` - Get database statistics
  - Returns total events, clubs, and category breakdown

### Health Check
- `GET /api/health` - Health check with database status
  - Returns backend status and database connection info
  - Includes database statistics if connected

### Example Endpoints
- `GET /api/example` - Example GET endpoint
- `POST /api/example` - Example POST endpoint

## Development

### Backend
- The Flask server runs on port 43798 (mapped from internal port 5000 in Docker)
- CORS is enabled for cross-origin requests
- Database queries are handled through [backend/database.py](backend/database.py)
- Add new routes in [backend/main.py](backend/main.py)
- All data is now served from PostgreSQL database

### Frontend
- Built with React and Vite
- Axios is configured for API calls in [frontend/src/services/api.js](frontend/src/services/api.js)
- Vite proxy configuration forwards `/api` requests to the backend
- Add new components in `frontend/src/components/`

### Key Design Decisions

**Consolidated Configuration:**
- **Single [requirements.txt](requirements.txt)** at root - Contains both web scraper and Flask backend dependencies
- **Single [.gitignore](.gitignore)** at root - Consolidated Python, Node, OS, and IDE ignore rules
- **Environment variables** set in [docker-compose.yml](docker-compose.yml) - No `.env` files needed for Docker
- **Build context** set to root in docker-compose - Allows Dockerfiles to access root-level files

**Port Configuration:**
- Docker: Backend accessible at `localhost:43798` (mapped from internal 5000)
- Manual: Backend runs on `localhost:5000` by default
- Frontend always on `localhost:3000`

---

## ASU Sun Devil Central Events Scraper

A Python-based web scraper for fetching event data from ASU Sun Devil Central using their API.

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure authentication**:
   - Copy `utils/.env.example` to `utils/.env`
   - Get your authentication cookies:
     1. Log into [Sun Devil Central](https://sundevilcentral.eoss.asu.edu/events)
     2. Open Browser DevTools (F12)
     3. Go to Network tab
     4. Refresh the page
     5. Find the `mobile_events_list` API call
     6. Right-click → Copy → Copy as cURL
     7. Extract the cookie string from the `-b` flag
   - Paste the cookie string into `utils/.env`:
     ```
     COOKIE_STRING=your_cookie_string_here
     ```

### Usage

**Basic usage (saves to `data/scraped_events.json`):**
```bash
python utils/scraper.py
```

**Custom output file:**
```bash
python utils/scraper.py path/to/output.json
```

### Output Format

The scraper fetches all events (both upcoming and past) and saves them as JSON with the following structure:

```json
[
  {
    "event_id": "123456",
    "event_uid": "abc-def-ghi",
    "name": "Event Name",
    "dates": "Nov 5, 2024, 6:00 PM - 8:00 PM",
    "category": "Social",
    "location": "Memorial Union",
    "club_id": "789",
    "club_name": "Example Club",
    "attendees": "15",
    "picture_url": "https://...",
    "price_range": "Free",
    "event_url": "https://sundevilcentral.eoss.asu.edu/event/...",
    "timezone": "America/Phoenix"
  }
]
```

### Features

- Automatic pagination to fetch all events
- Cookie-based authentication via environment variables
- Automatic creation of output directories
- Clean, parsed event data structure
- Progress feedback during scraping

### Scraper Setup

The scraper requires authentication cookies which should be placed in `utils/.env`:

1. Copy the template:
   ```bash
   cp utils/.env.example utils/.env
   ```

2. Add your credentials to `utils/.env` (see Configuration section above)

### Notes

- Authentication cookies expire periodically - you'll need to update `utils/.env` when they do
- The `utils/.env` file is gitignored to protect your credentials
- The scraper outputs to `data/scraped_events.json` by default (the `data/` directory is also gitignored)
