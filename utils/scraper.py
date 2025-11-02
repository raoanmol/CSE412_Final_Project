'''
ASU Sun Devil Central Events API Scraper
Fetches events data from the API endpoint and saves to JSON file.
'''

import requests
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv


class ASUEventsScraper:
    def __init__(self, cookies):
        '''
        Initialize the scraper with authentication cookies.

        Args:
            cookies (dict): Dictionary of cookies for authentication
        '''
        self.base_url = 'https://sundevilcentral.eoss.asu.edu/mobile_ws/v17/mobile_events_list'
        self.cookies = cookies
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://sundevilcentral.eoss.asu.edu/events',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }

    def fetch_events(self, range_start=0, limit=40):
        '''
        Fetch events from the API.

        Args:
            range_start (int): Starting index for pagination
            limit (int): Number of events to fetch per request

        Returns:
            list: List of event objects
        '''
        params = {
            'range': range_start,
            'limit': limit,
            'filter4_contains': 'OR',
            'filter4_notcontains': 'OR',
            'order': 'undefined',
            'search_word': '',
            '_': int(datetime.now().timestamp() * 1000)
        }

        try:
            print(f'Fetching events (range: {range_start}, limit: {limit})...')
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            print(f'✓ Successfully fetched {len(data)} items from API')
            return data

        except requests.exceptions.RequestException as e:
            print(f'✗ Error fetching events: {e}')
            return []
        except json.JSONDecodeError as e:
            print(f'✗ Error parsing JSON response: {e}')
            return []

    def fetch_all_events(self, max_events=None):
        '''
        Fetch all events by paginating through the API.

        Args:
            max_events (int): Maximum number of events to fetch (None for all)

        Returns:
            list: List of all event objects
        '''
        all_events = []
        range_start = 0
        limit = 40
        consecutive_empty = 0

        while True:
            events = self.fetch_events(range_start, limit)

            if not events:
                print('No more data returned from API')
                break

            actual_events = [e for e in events if e.get('listingSeparator') != 'true']

            if not actual_events:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print('No actual events in last 3 API calls, stopping pagination')
                    break
            else:
                consecutive_empty = 0
                all_events.extend(actual_events)
                print(f'  → Added {len(actual_events)} events. Total so far: {len(all_events)}')

            if max_events and len(all_events) >= max_events:
                all_events = all_events[:max_events]
                break

            if len(events) < limit and consecutive_empty > 0:
                print('API returned fewer items than requested, likely at end')
                break

            range_start += limit

        return all_events

    def parse_event(self, event_data):
        '''
        Parse event data into a cleaner format.

        Args:
            event_data (dict): Raw event data from API

        Returns:
            dict: Cleaned event data
        '''
        return {
            'event_id': event_data.get('p1'),
            'event_uid': event_data.get('p2'),
            'name': event_data.get('p3'),
            'dates': event_data.get('p4'),
            'category': event_data.get('p5'),
            'location': event_data.get('p6'),
            'club_id': event_data.get('p7'),
            'club_login': event_data.get('p8'),
            'club_name': event_data.get('p9'),
            'attendees': event_data.get('p10'),
            'picture_url': event_data.get('p11'),
            'price_range': event_data.get('p12'),
            'button_label': event_data.get('p13'),
            'badges': event_data.get('p14'),
            'event_url': f"https://sundevilcentral.eoss.asu.edu{event_data.get('p18')}" if event_data.get('p18') else None,
            'timezone': event_data.get('p28'),
            'aria_details': event_data.get('p29'),
        }

    def save_events(self, events, output_file='events.json', parse=True):
        '''
        Save events to a JSON file.

        Args:
            events (list): List of event objects
            output_file (str): Output file path
            parse (bool): Whether to parse events into cleaner format
        '''
        if parse:
            events = [self.parse_event(e) for e in events]

        try:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f'Created directory: {output_dir}')

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)

            print(f'\n✓ Saved {len(events)} events to: {output_file}')

        except Exception as e:
            print(f'✗ Error saving events: {e}')


def parse_cookies(cookie_string):
    '''
    Parse cookie string from browser into a dictionary.

    Args:
        cookie_string (str): Cookie string from browser (copy as cURL format)

    Returns:
        dict: Dictionary of cookies
    '''
    cookies = {}
    for item in cookie_string.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value
    return cookies


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    dotenv_path = os.path.join(project_root, 'utils', '.env')
    load_dotenv(dotenv_path)

    COOKIE_STRING = os.getenv('COOKIE_STRING')

    if not COOKIE_STRING:
        print('✗ Error: COOKIE_STRING not found in environment variables')
        print('\nPlease create a .env file with your authentication cookies:')
        print('  1. Copy .env.example to .env')
        print('  2. Add your cookie string from browser Dev Tools')
        print('\nSee .env.example for details')
        sys.exit(1)

    default_output = os.path.join(project_root, 'data', 'scraped_events.json')

    output_file = sys.argv[1] if len(sys.argv) > 1 else default_output

    cookies = parse_cookies(COOKIE_STRING)

    scraper = ASUEventsScraper(cookies)

    print('\nScraping ALL events from ASU Sun Devil Central...')
    print('='*60)

    events = scraper.fetch_all_events()

    if events:
        scraper.save_events(events, output_file)

        print('\n' + '='*60)
        print('SUMMARY:')
        print(f'  Total events scraped: {len(events)}')
        print(f'  Output file: {output_file}')

    else:
        print('\n✗ No events were scraped. Check your cookies and authentication.')
        sys.exit(1)
