#!/usr/bin/env python3
"""
Automated test suite for the Odoo Inventory API.
Tests both the Lambda function directly and the local server.
"""

import os
import sys
import json
import time
import requests
import pytest
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from list_inventory_lambda import lambda_handler

# Load environment variables
load_dotenv()

class TestLambdaFunction:
    """Test the Lambda function directly."""
    
    def create_event(self, method='GET', query_params=None, headers=None, body=None):
        """Create a mock Lambda event."""
        return {
            'requestContext': {
                'http': {
                    'method': method
                }
            },
            'queryStringParameters': query_params,
            'headers': headers or {},
            'body': body
        }
    
    def test_cors_preflight(self):
        """Test CORS preflight request."""
        event = self.create_event(method='OPTIONS')
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 204
        assert 'Access-Control-Allow-Origin' in response.get('headers', {})
        print("✅ CORS preflight test passed")
    
    def test_basic_inventory_list(self):
        """Test basic inventory listing."""
        event = self.create_event()
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'pagination' in body
        assert isinstance(body['data'], list)
        
        print(f"✅ Basic inventory test passed - {len(body['data'])} products returned")
        
        # Test product structure
        if body['data']:
            product = body['data'][0]
            required_fields = ['id', 'name', 'price', 'cost_price', 'currency', 'tags']
            for field in required_fields:
                assert field in product, f"Missing field: {field}"
            
            print(f"✅ Product structure test passed - Sample: {product['name']}")
    
    def test_pagination(self):
        """Test pagination parameters."""
        event = self.create_event(query_params={'limit': '5', 'offset': '0'})
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert len(body['data']) <= 5
        assert body['pagination']['limit'] == 5
        assert body['pagination']['offset'] == 0
        
        print("✅ Pagination test passed")
    
    def test_search_functionality(self):
        """Test search functionality."""
        # First get some products to find a search term
        event = self.create_event(query_params={'limit': '1'})
        response = lambda_handler(event, {})
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            if body['data']:
                # Use first word of first product name as search term
                search_term = body['data'][0]['name'].split()[0]
                
                # Now test search
                search_event = self.create_event(query_params={'search': search_term})
                search_response = lambda_handler(search_event, {})
                
                assert search_response['statusCode'] == 200
                search_body = json.loads(search_response['body'])
                assert search_body['filters_applied']['search_term'] == search_term
                
                print(f"✅ Search test passed - searched for '{search_term}'")
    
    def test_authentication_if_enabled(self):
        """Test authentication if CLIENT_ID and CLIENT_SECRET are set."""
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
        
        if not (client_id and client_secret):
            print("⏭️  Skipping auth test - CLIENT_ID/CLIENT_SECRET not set")
            return
        
        # Test with correct credentials
        event = self.create_event(headers={
            'x-client-id': client_id,
            'x-client-secret': client_secret
        })
        response = lambda_handler(event, {})
        assert response['statusCode'] == 200
        
        # Test with wrong credentials
        event = self.create_event(headers={
            'x-client-id': 'wrong',
            'x-client-secret': 'wrong'
        })
        response = lambda_handler(event, {})
        assert response['statusCode'] == 401
        
        print("✅ Authentication test passed")
    
    def test_method_not_allowed(self):
        """Test unsupported HTTP methods."""
        event = self.create_event(method='DELETE')
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 405
        print("✅ Method not allowed test passed")

class TestLocalServer:
    """Test the local Flask server."""
    
    @pytest.fixture(scope="class", autouse=True)
    def server_url(self):
        """Get server URL from environment or use default."""
        port = os.environ.get('LOCAL_PORT', '8000')
        return f"http://localhost:{port}"
    
    def test_health_endpoint(self, server_url):
        """Test health check endpoint."""
        try:
            response = requests.get(f"{server_url}/health", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'healthy'
            print("✅ Health endpoint test passed")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Local server not running - start with 'python local_server.py'")
    
    def test_inventory_endpoint(self, server_url):
        """Test inventory endpoint via HTTP."""
        try:
            response = requests.get(f"{server_url}/inventory", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            assert 'data' in data
            
            print(f"✅ HTTP inventory test passed - {len(data['data'])} products")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Local server not running")
    
    def test_inventory_with_params(self, server_url):
        """Test inventory endpoint with query parameters."""
        try:
            params = {'limit': 3, 'offset': 0}
            response = requests.get(f"{server_url}/inventory", params=params, timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert len(data['data']) <= 3
            
            print("✅ HTTP inventory with params test passed")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Local server not running")
    
    def test_cors_headers(self, server_url):
        """Test CORS headers in HTTP response."""
        try:
            response = requests.options(f"{server_url}/inventory", timeout=5)
            assert response.status_code == 204
            assert 'Access-Control-Allow-Origin' in response.headers
            
            print("✅ HTTP CORS test passed")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Local server not running")

def run_manual_tests():
    """Run tests manually without pytest."""
    print("🧪 Running Manual Test Suite")
    print("=" * 50)
    
    # Test Lambda function directly
    print("\n📦 Testing Lambda Function Directly:")
    lambda_tests = TestLambdaFunction()
    
    try:
        lambda_tests.test_cors_preflight()
        lambda_tests.test_basic_inventory_list()
        lambda_tests.test_pagination()
        lambda_tests.test_search_functionality()
        lambda_tests.test_authentication_if_enabled()
        lambda_tests.test_method_not_allowed()
        print("✅ All Lambda function tests passed!")
        
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
        return False
    
    # Test local server if running
    print("\n🌐 Testing Local Server (if running):")
    port = os.environ.get('LOCAL_PORT', '8000')
    server_url = f"http://localhost:{port}"
    
    try:
        response = requests.get(f"{server_url}/health", timeout=2)
        if response.status_code == 200:
            server_tests = TestLocalServer()
            server_tests.test_health_endpoint(server_url)
            server_tests.test_inventory_endpoint(server_url)
            server_tests.test_inventory_with_params(server_url)
            server_tests.test_cors_headers(server_url)
            print("✅ All server tests passed!")
        else:
            print("❌ Server responded with error")
            
    except requests.exceptions.ConnectionError:
        print("⏭️  Local server not running - start with 'python local_server.py'")
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    
    print("\n🎉 Manual test suite completed!")
    return True

if __name__ == "__main__":
    # Check environment
    required_vars = ['ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME', 'ODOO_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file based on .env.example")
        sys.exit(1)
    
    run_manual_tests()