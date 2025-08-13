#!/usr/bin/env python3
"""
Local Flask server to test the Lambda function.
This creates a REST API endpoint that you can test with Postman.
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Add parent directory to path to import the lambda function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from list_inventory_lambda import lambda_handler

# Load environment variables
load_dotenv()

app = Flask(__name__)

def create_lambda_event(flask_request):
    """Convert Flask request to Lambda event format."""
    
    # Get HTTP method
    method = flask_request.method
    
    # Get query parameters
    query_params = dict(flask_request.args) if flask_request.args else None
    
    # Get headers
    headers = dict(flask_request.headers)
    
    # Get body
    body = None
    if flask_request.data:
        try:
            body = flask_request.data.decode('utf-8')
        except:
            body = str(flask_request.data)
    
    # Create Lambda event structure
    event = {
        'requestContext': {
            'http': {
                'method': method
            }
        },
        'queryStringParameters': query_params,
        'headers': headers,
        'body': body
    }
    
    return event

@app.route('/inventory', methods=['GET', 'POST', 'OPTIONS'])
def inventory_endpoint():
    """Main inventory endpoint that mimics Lambda Function URL."""
    
    try:
        # Create Lambda event from Flask request
        event = create_lambda_event(request)
        context = {}  # Mock Lambda context
        
        # Debug authentication
        print(f"🔍 Debug - Request headers: {dict(request.headers)}")
        print(f"🔍 Debug - CLIENT_ID from env: '{os.environ.get('CLIENT_ID')}'")
        print(f"🔍 Debug - CLIENT_SECRET from env: '{os.environ.get('CLIENT_SECRET')}'")
        print(f"🔍 Debug - Received x-client-id: '{request.headers.get('x-client-id')}'")
        print(f"🔍 Debug - Received x-client-secret: '{request.headers.get('x-client-secret')}'")
        
        # Call the Lambda handler
        response = lambda_handler(event, context)
        
        # Extract response components
        status_code = response.get('statusCode', 500)
        body = response.get('body', '{}')
        headers = response.get('headers', {})
        
        # Parse body if it's a string
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except:
                pass
        
        # Create Flask response
        flask_response = jsonify(body)
        flask_response.status_code = status_code
        
        # Add headers
        for key, value in headers.items():
            flask_response.headers[key] = value
        
        return flask_response
        
    except Exception as e:
        print(f"Error in local server: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Odoo Inventory API Local Server',
        'environment_check': {
            'ODOO_URL': bool(os.environ.get('ODOO_URL')),
            'ODOO_DB': bool(os.environ.get('ODOO_DB')),
            'ODOO_USERNAME': bool(os.environ.get('ODOO_USERNAME')),
            'ODOO_PASSWORD': bool(os.environ.get('ODOO_PASSWORD')),
            'CLIENT_ID': bool(os.environ.get('CLIENT_ID')),
            'CLIENT_SECRET': bool(os.environ.get('CLIENT_SECRET'))
        }
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation."""
    return jsonify({
        'message': 'Odoo Inventory API Local Server',
        'endpoints': {
            'GET /inventory': 'List inventory items',
            'GET /inventory?limit=10&offset=0': 'List with pagination',
            'GET /inventory?search=laptop': 'Search products',
            'GET /inventory?category_id=5': 'Filter by category',
            'GET /health': 'Health check',
            'OPTIONS /inventory': 'CORS preflight'
        },
        'authentication': {
            'headers': {
                'x-client-id': 'your_client_id',
                'x-client-secret': 'your_client_secret'
            }
        }
    })

if __name__ == '__main__':
    # Check environment variables
    required_vars = ['ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME', 'ODOO_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file based on .env.example")
        sys.exit(1)
    
    port = int(os.environ.get('LOCAL_PORT', 8000))
    
    print("🚀 Starting Odoo Inventory API Local Server")
    print(f"🔗 Server URL: http://localhost:{port}")
    print(f"📋 API Endpoint: http://localhost:{port}/inventory")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    print(f"🔧 Connected to Odoo: {os.environ.get('ODOO_URL')}")
    print("\n💡 Test with Postman or curl:")
    print(f"   curl http://localhost:{port}/inventory")
    print(f"   curl http://localhost:{port}/inventory?limit=5")
    print(f"   curl http://localhost:{port}/inventory?search=laptop")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=port, debug=True)