#!/usr/bin/env python3
"""
Comprehensive test script for all Odoo Inventory Lambda APIs
"""

import requests
import json
import time

# API Configuration
BASE_URL = "https://your-lambda-function-url.amazonaws.com"
HEADERS = {
    "x-client-id": "your_client_id",
    "x-client-secret": "your_client_secret",
    "Content-Type": "application/json"
}

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"{'='*60}")

def print_response(response, show_data=True):
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        if show_data:
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Success: {data.get('success', 'N/A')}")
            if 'message' in data:
                print(f"Message: {data['message']}")
            if 'data' in data and isinstance(data['data'], list):
                print(f"Items returned: {len(data['data'])}")
    except:
        print(f"Raw Response: {response.text}")
    print("-" * 60)

def test_list_inventory_get():
    """Test GET / - List inventory with query parameters"""
    print_test_header("List Inventory (GET)")
    
    # Test basic listing
    print("📋 Basic inventory listing:")
    response = requests.get(f"{BASE_URL}/", headers=HEADERS)
    print_response(response, show_data=False)
    
    # Test with search
    print("🔍 Search for CHANA:")
    response = requests.get(f"{BASE_URL}/?search=CHANA&limit=5", headers=HEADERS)
    print_response(response, show_data=False)
    
    return response.status_code == 200

def test_search_inventory_post():
    """Test POST / - Search inventory with JSON body"""
    print_test_header("Search Inventory (POST)")
    
    # Test search by product name
    search_data = {
        "product_name": "CHANA",
        "limit": 3
    }
    
    print("🔍 Search with JSON body:")
    response = requests.post(f"{BASE_URL}/", headers=HEADERS, json=search_data)
    print_response(response, show_data=False)
    
    return response.status_code == 200

def test_list_tags():
    """Test GET /tags - List all tags"""
    print_test_header("List Tags (GET)")
    
    print("🏷️ Listing all tags:")
    response = requests.get(f"{BASE_URL}/tags", headers=HEADERS)
    print_response(response, show_data=False)
    
    # Test search tags
    print("🔍 Search tags with 'premium':")
    response = requests.get(f"{BASE_URL}/tags?search=premium&limit=3", headers=HEADERS)
    print_response(response, show_data=False)
    
    return response.status_code == 200

def test_create_tag():
    """Test POST /tags - Create new tag"""
    print_test_header("Create Tag (POST)")
    
    # Create a test tag
    tag_data = {
        "name": f"Test Tag {int(time.time())}",
        "color": 5
    }
    
    print(f"🏷️ Creating tag: {tag_data['name']}")
    response = requests.post(f"{BASE_URL}/tags", headers=HEADERS, json=tag_data)
    print_response(response)
    
    if response.status_code == 201:
        try:
            return response.json()['data']['id']  # Return tag ID for later use
        except:
            return True
    return False

def test_create_product(tag_id=None):
    """Test POST /products - Create new product"""
    print_test_header("Create Product (POST)")
    
    # Create a test product
    product_data = {
        "name": f"Test Product {int(time.time())}",
        "cost": 99.99
    }
    
    if tag_id:
        product_data["tag_ids"] = [tag_id]
        print(f"📦 Creating product with tag ID {tag_id}: {product_data['name']}")
    else:
        print(f"📦 Creating product: {product_data['name']}")
    
    response = requests.post(f"{BASE_URL}/products", headers=HEADERS, json=product_data)
    print_response(response)
    
    if response.status_code == 201:
        try:
            return response.json()['data']['name']  # Return product name for later use
        except:
            return True
    return False

def test_update_product(product_name):
    """Test PUT /products - Update product price"""
    print_test_header("Update Product (PUT)")
    
    if not product_name:
        print("⚠️ No product name provided, skipping update test")
        return False
    
    # Update product price
    update_data = {
        "product_name": product_name,
        "price": 149.99,
        "update_cost_price": False
    }
    
    print(f"💰 Updating price for: {product_name}")
    response = requests.put(f"{BASE_URL}/products", headers=HEADERS, json=update_data)
    print_response(response)
    
    return response.status_code == 200

def test_error_cases():
    """Test error handling"""
    print_test_header("Error Handling Tests")
    
    # Test unauthorized access
    print("🚫 Testing unauthorized access:")
    bad_headers = {"Content-Type": "application/json"}
    response = requests.get(f"{BASE_URL}/", headers=bad_headers)
    print_response(response, show_data=False)
    
    # Test invalid JSON
    print("❌ Testing invalid JSON:")
    response = requests.post(f"{BASE_URL}/tags", headers=HEADERS, data="invalid json")
    print_response(response, show_data=False)
    
    # Test missing required fields
    print("📝 Testing missing required fields:")
    response = requests.post(f"{BASE_URL}/products", headers=HEADERS, json={})
    print_response(response, show_data=False)
    
    return True

def test_cors():
    """Test CORS preflight"""
    print_test_header("CORS Preflight Test")
    
    cors_headers = {
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "x-client-id,x-client-secret,content-type"
    }
    
    print("🌐 Testing CORS preflight:")
    response = requests.options(f"{BASE_URL}/", headers=cors_headers)
    print_response(response, show_data=False)
    
    return response.status_code == 204

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive API testing...")
    print(f"🔗 Base URL: {BASE_URL}")
    print(f"🔐 Using authentication: {HEADERS['x-client-id']}")
    
    results = {}
    
    # Test all endpoints
    results['list_inventory_get'] = test_list_inventory_get()
    results['search_inventory_post'] = test_search_inventory_post()
    results['list_tags'] = test_list_tags()
    
    # Create tag and get ID for product creation
    tag_id = test_create_tag()
    results['create_tag'] = bool(tag_id)
    
    # Create product and get name for price update
    product_name = test_create_product(tag_id if isinstance(tag_id, int) else None)
    results['create_product'] = bool(product_name)
    
    # Update product price
    results['update_product'] = test_update_product(product_name if isinstance(product_name, str) else None)
    
    # Test error cases
    results['error_handling'] = test_error_cases()
    results['cors'] = test_cors()
    
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