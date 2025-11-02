from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

def load_events():
    docker_path = '/data/scraped_events.json'

    if os.path.exists(docker_path):
        events_path = docker_path
        print(f'Running in Docker, using: {events_path}')
    else:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        events_path = os.path.join(project_root, 'data', 'scraped_events.json')
        print(f'Running locally, using: {events_path}')

    print(f'Looking for events at: {events_path}')
    print(f'File exists: {os.path.exists(events_path)}')

    try:
        with open(events_path, 'r') as f:
            data = json.load(f)
            print(f'Successfully loaded {len(data)} events')
            return data
    except Exception as e:
        print(f'Error loading events: {e}')
        print(f'Current working directory: {os.getcwd()}')
        return []

EVENTS_DATA = load_events()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running!'})

@app.route('/api/events', methods=['GET'])
def get_events():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    paginated_events = EVENTS_DATA[start_idx:end_idx]

    total_events = len(EVENTS_DATA)
    total_pages = (total_events + limit - 1) // limit

    return jsonify({
        'events': paginated_events,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_events': total_events,
            'limit': limit,
            'has_more': end_idx < total_events
        }
    })

@app.route('/api/example', methods=['GET'])
def get_example():
    return jsonify({
        'message': 'This is an example GET endpoint',
        'data': []
    })

@app.route('/api/example', methods=['POST'])
def post_example():
    data = request.get_json()
    return jsonify({
        'message': 'Data received successfully',
        'received': data
    }), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
