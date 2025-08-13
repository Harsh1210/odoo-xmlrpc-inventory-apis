#!/usr/bin/env python3
"""
Quick test for the update product API fix
Uses environment variables for secure testing
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration from environment variables
BASE_URL = os.environ.get('LAMBDA_FUNCTION_URL', 'https://your-lambda-function-url.amazonaws.com')
HEADERS = {
    "x-client-id": os.environ.get('CLIENT_ID', 'your_client_id'),
    "x-client-secret": os.environ.get('CLIENT_SECRET', 'your_client_secret'),
    "Content-Type": "application/json"
}

def test_update_product():
    """Test the update product API"""
    
    print("🧪 Testing Update Product API (Fixed)")
    print("=" * 50)
    
    # Test data
    update_data = {
        "product_name": "CHANA GOLD",
        "price": 7200,
        "update_cost_price": False
    }
    
    print(f"Testing PUT method...")
    print(f"Request: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(f"{BASE_URL}/products", headers=HEADERS, json=update_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print("❌ FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw Error: {response.text}")
                
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_update_product()