from flask import Flask, jsonify, request
from flask_cors import CORS
import database as db

app = Flask(__name__)
CORS(app)

print('Checking database connection...')
if db.check_database_connection():
    print('✓ Database connection successful!')
    stats = db.get_database_stats()
    print(f'✓ Database has {stats["total_events"]} events and {stats["total_clubs"]} clubs')
else:
    print('✗ Warning: Database connection failed!')
    print('  Make sure PostgreSQL is running and DATABASE_URL is set correctly')

@app.route('/api/health', methods=['GET'])
def health_check():
    '''Health check endpoint with database status.'''
    db_connected = db.check_database_connection()

    response = {
        'status': 'healthy' if db_connected else 'degraded',
        'message': 'Backend is running!',
        'database': 'connected' if db_connected else 'disconnected'
    }

    if db_connected:
        try:
            stats = db.get_database_stats()
            response['stats'] = stats
        except Exception as e:
            response['database'] = 'error'
            response['error'] = str(e)

    return jsonify(response)

@app.route('/api/events', methods=['GET'])
def get_events():
    '''
    Get paginated events from database.

    Query parameters:
        - page: Page number (default: 1)
        - limit: Events per page (default: 20, max: 100)
        - category: Filter by category (optional)
        - search: Search in event names (optional)
    '''
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category', None, type=str)
        search = request.args.get('search', None, type=str)

        result = db.get_events_paginated(
            page=page,
            limit=limit,
            category=category,
            search=search
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch events',
            'message': str(e)
        }), 500

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    '''Get a single event by its ID.'''
    try:
        event = db.get_event_by_id(event_id)

        if event:
            return jsonify(event)
        else:
            return jsonify({
                'error': 'Event not found',
                'message': f'No event found with ID: {event_id}'
            }), 404

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch event',
            'message': str(e)
        }), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    '''Get all unique event categories.'''
    try:
        categories = db.get_categories()
        return jsonify({
            'categories': categories,
            'count': len(categories)
        })

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch categories',
            'message': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    '''Get database statistics.'''
    try:
        stats = db.get_database_stats()
        return jsonify(stats)

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch statistics',
            'message': str(e)
        }), 500


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
