# CSE412 Final Project

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
