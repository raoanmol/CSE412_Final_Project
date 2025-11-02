# CSE412 Final Project

A full-stack web application with a React frontend and Flask backend.

## Project Structure

```
.
├── backend/          # Flask backend server
│   ├── main.py      # Main Flask application
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React frontend application
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── services/
│   │       └── api.js
│   ├── package.json
│   └── vite.config.js
└── utils/           # Utility scripts
    └── scraper.py   # ASU Sun Devil Central Events Scraper
```

## Quick Start

### Option 1: Using Docker (Recommended)

**Prerequisites:** Make sure you have [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

1. Start the application:
   ```bash
   make up
   ```

That's it! The command will:
- Build Docker images for both frontend and backend
- Start both containers
- Set up networking between them
- Frontend will be available at `http://localhost:3000`
- Backend will be available at `http://localhost:43798`

**Other useful commands:**
```bash
make down            # Stop the application
make logs            # View logs from both containers
make logs-backend    # View only backend logs
make logs-frontend   # View only frontend logs
make restart         # Restart the application
make build           # Rebuild containers (use after changing dependencies)
make clean           # Remove all containers and volumes
make help            # See all available commands
```

**How it works:**
- Docker creates isolated "containers" (like lightweight virtual machines) for your frontend and backend
- Each container has its own environment with all dependencies installed
- The containers can talk to each other through a virtual network
- Your code is "mounted" into the containers, so changes you make are reflected immediately (hot-reload)
- No need to install Python, Node, or any dependencies on your machine!

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

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the backend server:
   ```bash
   python main.py
   ```

The backend will start on `http://localhost:43798`

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

## API Endpoints

The backend currently includes these example endpoints:

- `GET /api/health` - Health check endpoint
- `GET /api/example` - Example GET endpoint
- `POST /api/example` - Example POST endpoint

## Development

### Backend
- The Flask server runs on port 43798 (mapped from internal port 5000 in Docker)
- CORS is enabled for cross-origin requests
- Add new routes in [backend/main.py](backend/main.py)

### Frontend
- Built with React and Vite
- Axios is configured for API calls in [frontend/src/services/api.js](frontend/src/services/api.js)
- Vite proxy configuration forwards `/api` requests to the backend
- Add new components in `frontend/src/components/`

---

## ASU Sun Devil Central Events Scraper

A Python-based web scraper for fetching event data from ASU Sun Devil Central using their API.

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure authentication**:
   - Copy `.env.example` to `.env`
   - Get your authentication cookies:
     1. Log into [Sun Devil Central](https://sundevilcentral.eoss.asu.edu/events)
     2. Open Browser DevTools (F12)
     3. Go to Network tab
     4. Refresh the page
     5. Find the `mobile_events_list` API call
     6. Right-click → Copy → Copy as cURL
     7. Extract the cookie string from the `-b` flag
   - Paste the cookie string into `.env`:
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

### Project Structure

```
.
├── utils/
│   └── scraper.py           # Main scraper script
│   └── .env                 # Your credentials (gitignored)
│   └── .env.example         # Template for credentials
├── data/
│   └── scraped_events.json  # Default output location
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Notes

- Authentication cookies expire periodically - you'll need to update `.env` when they do
- The `.env` file is gitignored to protect your credentials
