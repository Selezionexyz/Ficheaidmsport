#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import ssl

# Load environment variables
load_dotenv('/app/backend/.env')
mongo_url = os.environ.get('MONGO_URL')

print(f"Testing MongoDB connection...")
print(f"MONGO_URL: {mongo_url[:50]}..." if mongo_url else "MONGO_URL not found")

if not mongo_url:
    print("❌ MONGO_URL environment variable not found!")
    sys.exit(1)

try:
    # Test with pymongo directly
    print("Attempting connection with pymongo...")
    
    # Try different SSL configurations
    ssl_configs = [
        {"ssl_cert_reqs": ssl.CERT_NONE, "ssl_match_hostname": False},
        {"ssl": False},
        {}  # Default
    ]
    
    for i, ssl_config in enumerate(ssl_configs):
        try:
            print(f"\nTesting configuration {i+1}: {ssl_config}")
            client = MongoClient(mongo_url, **ssl_config)
            
            # Test the connection
            client.admin.command('ping')
            print(f"✅ Connection successful with config {i+1}!")
            
            # Test database access
            db = client[os.environ.get('DB_NAME', 'test')]
            collections = db.list_collection_names()
            print(f"✅ Database access successful! Collections: {collections}")
            break
            
        except Exception as e:
            print(f"❌ Config {i+1} failed: {e}")
    else:
        print("❌ All connection attempts failed!")
        
except Exception as e:
    print(f"❌ Error: {e}")