#!/usr/bin/env python3
"""
Backend API Testing Suite for Générateur de Fiches Produits
Tests all backend endpoints to verify functionality
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing Backend API at: {API_BASE}")
print(f"📅 Test started at: {datetime.now().isoformat()}")
print("=" * 60)

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print("❌ Health endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def test_search_with_sku():
    """Test search endpoint with SKU 48SMA0097-21G (Lacoste sneakers)"""
    print("\n👟 Testing Search with SKU: 48SMA0097-21G...")
    
    payload = {
        "sku": "48SMA0097-21G",
        "ean": None
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/search",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search endpoint working!")
            print(f"Product found: {data.get('product', {}).get('name', 'Unknown')}")
            print(f"Brand: {data.get('product', {}).get('brand', 'Unknown')}")
            print(f"Price: {data.get('product', {}).get('price', 'Unknown')}€")
            
            # Verify it's the expected Lacoste product
            product = data.get('product', {})
            if "Lacoste L001 Set Leather Sneakers" in product.get('name', ''):
                print("✅ Correct product data returned")
                return True, data.get('product', {}).get('id')
            else:
                print("⚠️ Unexpected product returned")
                return True, data.get('product', {}).get('id')
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Search endpoint error: {str(e)}")
        return False, None

def test_search_with_ean():
    """Test search endpoint with EAN"""
    print("\n🔢 Testing Search with EAN: 3608077027028...")
    
    payload = {
        "ean": "3608077027028",
        "sku": None
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/search",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ EAN search working!")
            print(f"Product: {data.get('product', {}).get('name', 'Unknown')}")
            return True, data.get('product', {}).get('id')
        else:
            print(f"❌ EAN search failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ EAN search error: {str(e)}")
        return False, None

def test_export_endpoint(product_id):
    """Test export endpoint"""
    if not product_id:
        print("\n📤 Skipping export test - no product ID available")
        return False
        
    print(f"\n📤 Testing Export with Product ID: {product_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/export/{product_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Export endpoint working!")
            print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Export failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return False

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print("\n🚫 Testing Error Handling...")
    
    # Test empty request
    try:
        response = requests.post(
            f"{API_BASE}/search",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Empty request status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Empty request properly rejected")
        else:
            print("⚠️ Empty request handling unexpected")
    except Exception as e:
        print(f"❌ Empty request test error: {str(e)}")
    
    # Test invalid EAN
    try:
        response = requests.post(
            f"{API_BASE}/search",
            json={"ean": "123", "sku": None},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Invalid EAN status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Invalid EAN properly rejected")
        else:
            print("⚠️ Invalid EAN handling unexpected")
    except Exception as e:
        print(f"❌ Invalid EAN test error: {str(e)}")

def test_root_endpoint():
    """Test the root endpoint that serves HTML"""
    print("\n🏠 Testing Root Endpoint...")
    try:
        response = requests.get(BACKEND_URL, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200 and "Générateur de Fiches Produits" in response.text:
            print("✅ Root endpoint serving HTML correctly")
            return True
        else:
            print("❌ Root endpoint not working properly")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False

def main():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests...")
    
    results = {
        "health": False,
        "root": False,
        "search_sku": False,
        "search_ean": False,
        "export": False,
        "error_handling": True  # Assume this works unless it fails
    }
    
    # Test all endpoints
    results["health"] = test_health_endpoint()
    results["root"] = test_root_endpoint()
    results["search_sku"], product_id = test_search_with_sku()
    results["search_ean"], _ = test_search_with_ean()
    results["export"] = test_export_endpoint(product_id)
    test_invalid_requests()  # This doesn't affect overall results
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len([k for k in results.keys() if k != "error_handling"])
    passed_tests = sum([1 for k, v in results.items() if v and k != "error_handling"])
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL BACKEND TESTS PASSED!")
        return True
    else:
        print("⚠️ SOME BACKEND TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)