from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import mongo

webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=['POST'])
def receiver():
    """
    Webhook receiver endpoint for GitHub events
    Handles PUSH, PULL_REQUEST, and MERGE actions
    """
    try:
        # Get the JSON payload from GitHub webhook
        payload = request.json
        
        # Get the event type from GitHub headers
        event_type = request.headers.get('X-GitHub-Event', '')
        
        # Initialize the document to store in MongoDB
        webhook_data = {
            'request_id': None,
            'author': None,
            'action': None,
            'from_branch': None,
            'to_branch': None,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Process based on event type
        if event_type == 'push':
            # Extract push event data
            webhook_data['action'] = 'PUSH'
            webhook_data['author'] = payload.get('pusher', {}).get('name', 'Unknown')
            
            # Extract branch name from ref (refs/heads/branch-name)
            ref = payload.get('ref', '')
            branch = ref.split('/')[-1] if '/' in ref else ref
            webhook_data['to_branch'] = branch
            
            # Use commit SHA as request_id
            if payload.get('head_commit'):
                webhook_data['request_id'] = payload['head_commit'].get('id', '')
            
        elif event_type == 'pull_request':
            pr_data = payload.get('pull_request', {})
            action = payload.get('action', '')
            
            # Only process opened/reopened pull requests
            if action in ['opened', 'reopened']:
                webhook_data['action'] = 'PULL_REQUEST'
                webhook_data['author'] = pr_data.get('user', {}).get('login', 'Unknown')
                webhook_data['from_branch'] = pr_data.get('head', {}).get('ref', '')
                webhook_data['to_branch'] = pr_data.get('base', {}).get('ref', '')
                webhook_data['request_id'] = str(pr_data.get('number', ''))
                
            elif action == 'closed' and pr_data.get('merged', False):
                # Handle merge action
                webhook_data['action'] = 'MERGE'
                webhook_data['author'] = pr_data.get('merged_by', {}).get('login', 'Unknown')
                webhook_data['from_branch'] = pr_data.get('head', {}).get('ref', '')
                webhook_data['to_branch'] = pr_data.get('base', {}).get('ref', '')
                webhook_data['request_id'] = str(pr_data.get('number', ''))
            else:
                # Ignore other pull request actions
                return jsonify({'message': 'Pull request action ignored'}), 200
        else:
            # Unsupported event type
            return jsonify({'message': f'Event type {event_type} not supported'}), 200
        
        # Insert into MongoDB
        if webhook_data['action']:
            result = mongo.db.actions.insert_one(webhook_data)
            
            return jsonify({
                'message': 'Webhook received successfully',
                'action': webhook_data['action'],
                'id': str(result.inserted_id)
            }), 200
        else:
            return jsonify({'message': 'No valid action found'}), 200
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@webhook.route('/events', methods=['GET'])
def get_events():
    """
    API endpoint to retrieve all events from MongoDB
    Used by the UI to display events
    """
    try:
        # Retrieve all events, sorted by timestamp (newest first)
        events = list(mongo.db.actions.find(
            {},
            {'_id': 0}  # Exclude MongoDB _id field
        ).sort('timestamp', -1))
        
        return jsonify({
            'events': events,
            'count': len(events)
        }), 200
        
    except Exception as e:
        print(f"Error retrieving events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@webhook.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200
