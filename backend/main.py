from flask import Flask, jsonify, request
from flask_cors import CORS
import database as db

app = Flask(__name__)
CORS(app)

print('Checking database connection...')
if db.check_database_connection():
    print('✓ Database connection successful!')
    stats = db.get_database_stats()
    print(f'✓ Database has {stats["total_events"]} events and {stats["total_organizations"]} organizations')
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
        - category: Filter by category (optional, can be comma-separated list)
        - search: Search in event names (optional)
        - event_type: Filter by event type (in_person, online, hybrid) (optional)
        - start_date: Filter events after this date (ISO format) (optional)
        - end_date: Filter events before this date (ISO format) (optional)
        - organization: Filter by organization ID (optional, can be comma-separated list)
    '''
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', None, type=str)
        event_type = request.args.get('event_type', None, type=str)
        start_date = request.args.get('start_date', None, type=str)
        end_date = request.args.get('end_date', None, type=str)

        # Handle comma-separated categories
        category = request.args.get('category', None, type=str)
        if category:
            category = [c.strip() for c in category.split(',')]

        # Handle comma-separated organizations
        organization = request.args.get('organization', None, type=str)
        if organization:
            organization = [o.strip() for o in organization.split(',')]

        result = db.get_events_paginated(
            page=page,
            limit=limit,
            category=category,
            search=search,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            organization=organization
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


@app.route('/api/organizations', methods=['GET'])
def get_organizations():
    '''
    Get all organizations with optional stats.

    Query parameters:
        - with_stats: Include event/member/officer counts (default: false)
        - search: Filter by organization name (optional)
        - sort_by: Sort by field (events, members, officers, name) (optional)
    '''
    try:
        with_stats = request.args.get('with_stats', 'false').lower() == 'true'

        if with_stats:
            search = request.args.get('search', None, type=str)
            sort_by = request.args.get('sort_by', None, type=str)
            organizations = db.get_organizations_with_stats(search=search, sort_by=sort_by)
        else:
            organizations = db.get_organizations()

        return jsonify({
            'organizations': organizations,
            'count': len(organizations)
        })

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch organizations',
            'message': str(e)
        }), 500


@app.route('/api/organizations/<org_id>', methods=['GET'])
def get_organization_detail(org_id):
    '''Get detailed information about a specific organization.'''
    try:
        org_details = db.get_organization_details(org_id)

        if org_details:
            return jsonify(org_details)
        else:
            return jsonify({
                'error': 'Organization not found',
                'message': f'No organization found with ID: {org_id}'
            }), 404

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch organization details',
            'message': str(e)
        }), 500


@app.route('/api/events', methods=['POST'])
def create_event():
    '''Create a new event.'''
    try:
        event_data = request.get_json()

        # Validate required fields
        required_fields = ['event_name', 'category', 'event_type', 'org_id']
        for field in required_fields:
            if not event_data.get(field):
                return jsonify({
                    'error': 'Validation error',
                    'message': f'Missing required field: {field}'
                }), 400

        created_event = db.create_event(event_data)
        return jsonify(created_event), 201

    except Exception as e:
        return jsonify({
            'error': 'Failed to create event',
            'message': str(e)
        }), 500


@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    '''Update an existing event.'''
    try:
        event_data = request.get_json()

        updated_event = db.update_event(event_id, event_data)

        if updated_event:
            return jsonify(updated_event), 200
        else:
            return jsonify({
                'error': 'Event not found',
                'message': f'No event found with ID: {event_id}'
            }), 404

    except Exception as e:
        return jsonify({
            'error': 'Failed to update event',
            'message': str(e)
        }), 500


@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    '''Delete an event.'''
    try:
        deleted = db.delete_event(event_id)

        if deleted:
            return jsonify({
                'message': 'Event deleted successfully',
                'event_id': event_id
            }), 200
        else:
            return jsonify({
                'error': 'Event not found',
                'message': f'No event found with ID: {event_id}'
            }), 404

    except Exception as e:
        return jsonify({
            'error': 'Failed to delete event',
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
