#!/usr/bin/env python3
"""
Production API test script for Odoo Inventory Lambda APIs
Uses environment variables for secure testing - safe for git
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration from environment variables
BASE_URL = os.environ.get('LAMBDA_FUNCTION_URL')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

HEADERS = {
    "x-client-id": CLIENT_ID,
    "x-client-secret": CLIENT_SECRET,
    "Content-Type": "application/json"
}

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['LAMBDA_FUNCTION_URL', 'CLIENT_ID', 'CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with your credentials")
        print("   Copy .env.template to .env and fill in your values")
        return False
    
    print("✅ All required environment variables are set")
    return True

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"{'='*60}")

def print_response(response, show_data=True):
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        if show_data and response.status_code in [200, 201]:
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Success: {data.get('success', 'N/A')}")
            if 'message' in data:
                print(f"Message: {data['message']}")
            if 'error' in data:
                print(f"Error: {data['error']}")
            if 'data' in data and isinstance(data['data'], list):
                print(f"Items returned: {len(data['data'])}")
    except:
        print(f"Raw Response: {response.text}")
    print("-" * 60)

def test_list_inventory():
    """Test GET / - List inventory"""
    print_test_header("List Inventory (GET)")
    
    try:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS)
        print_response(response, show_data=False)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_inventory():
    """Test POST / - Search inventory"""
    print_test_header("Search Inventory (POST)")
    
    search_data = {
        "product_name": "CHANA",
        "limit": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/", headers=HEADERS, json=search_data)
        print_response(response, show_data=False)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_tags():
    """Test GET /tags - List tags"""
    print_test_header("List Tags (GET)")
    
    try:
        response = requests.get(f"{BASE_URL}/tags", headers=HEADERS)
        print_response(response, show_data=False)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_tag():
    """Test POST /tags - Create tag"""
    print_test_header("Create Tag (POST)")
    
    tag_data = {
        "name": f"Test Tag {int(time.time())}",
        "color": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tags", headers=HEADERS, json=tag_data)
        print_response(response)
        
        if response.status_code == 201:
            try:
                return response.json()['data']['id']
            except:
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_product(tag_id=None):
    """Test POST /products - Create product"""
    print_test_header("Create Product (POST)")
    
    product_data = {
        "name": f"Test Product {int(time.time())}",
        "cost": 99.99
    }
    
    if tag_id:
        product_data["tag_ids"] = [tag_id]
    
    try:
        response = requests.post(f"{BASE_URL}/products", headers=HEADERS, json=product_data)
        print_response(response)
        
        if response.status_code == 201:
            try:
                return response.json()['data']['name']
            except:
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_update_product(product_name=None):
    """Test PUT /products - Update product"""
    print_test_header("Update Product (PUT)")
    
    if not product_name:
        # Try to find an existing product first
        print("🔍 Searching for existing product to update...")
        search_data = {"product_name": "CHANA", "limit": 1}
        
        try:
            search_response = requests.post(f"{BASE_URL}/", headers=HEADERS, json=search_data)
            if search_response.status_code == 200:
                search_result = search_response.json()
                if search_result.get('found') and search_result.get('data'):
                    product_name = search_result['data'][0]['name']
                    print(f"Found product to update: {product_name}")
                else:
                    print("⚠️ No existing products found to update")
                    return False
            else:
                print("⚠️ Could not search for products")
                return False
        except Exception as e:
            print(f"Search error: {e}")
            return False
    
    update_data = {
        "product_name": product_name,
        "price": 149.99,
        "update_cost_price": False
    }
    
    try:
        response = requests.put(f"{BASE_URL}/products", headers=HEADERS, json=update_data)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_update_product_with_post():
    """Test POST /products - Update product (alternative method)"""
    print_test_header("Update Product (POST method)")
    
    # Search for existing product first
    print("🔍 Searching for existing product to update...")
    search_data = {"product_name": "CHANA", "limit": 1}
    
    try:
        search_response = requests.post(f"{BASE_URL}/", headers=HEADERS, json=search_data)
        if search_response.status_code == 200:
            search_result = search_response.json()
            if search_result.get('found') and search_result.get('data'):
                product_name = search_result['data'][0]['name']
                print(f"Found product to update: {product_name}")
                
                update_data = {
                    "product_name": product_name,
                    "price": 199.99,
                    "update_cost_price": False
                }
                
                response = requests.post(f"{BASE_URL}/products", headers=HEADERS, json=update_data)
                print_response(response)
                return response.status_code == 200
            else:
                print("⚠️ No existing products found to update")
                return False
        else:
            print("⚠️ Could not search for products")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_error_handling():
    """Test error cases"""
    print_test_header("Error Handling")
    
    # Test unauthorized access
    print("🚫 Testing unauthorized access:")
    bad_headers = {"Content-Type": "application/json"}
    response = requests.get(f"{BASE_URL}/", headers=bad_headers)
    print_response(response, show_data=False)
    
    return response.status_code == 401

def main():
    """Run all tests"""
    print("🚀 Starting Production API Testing...")
    print(f"🔗 Base URL: {BASE_URL}")
    print(f"🔐 Client ID: {CLIENT_ID}")
    
    # Check environment first
    if not check_environment():
        return False
    
    results = {}
    
    # Test all endpoints
    print("\n" + "="*60)
    print("🧪 RUNNING ALL API TESTS")
    print("="*60)
    
    results['list_inventory'] = test_list_inventory()
    results['search_inventory'] = test_search_inventory()
    results['list_tags'] = test_list_tags()
    
    # Create tag and product
    tag_id = test_create_tag()
    results['create_tag'] = bool(tag_id)
    
    product_name = test_create_product(tag_id if isinstance(tag_id, int) else None)
    results['create_product'] = bool(product_name)
    
    # Test update methods
    results['update_product_put'] = test_update_product()
    results['update_product_post'] = test_update_product_with_post()
    
    # Test error handling
    results['error_handling'] = test_error_handling()
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()