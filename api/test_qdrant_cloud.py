#!/usr/bin/env python3
"""
Test script to verify Qdrant cloud configuration.
Usage: 
  QDRANT_MODE=cloud QDRANT_URL=your_url QDRANT_API_KEY=your_key python test_qdrant_cloud.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_qdrant_connection():
    # Set test environment variables if not already set
    if os.getenv("QDRANT_MODE") != "cloud":
        print("⚠️  QDRANT_MODE is not set to 'cloud'")
        print("Please set environment variables:")
        print("  export QDRANT_MODE=cloud")
        print("  export QDRANT_URL=https://your-cluster.us-east.aws.cloud.qdrant.io")
        print("  export QDRANT_API_KEY=your_api_key")
        return False

    # Import after environment is set
    from config.settings import get_settings
    from core.vector_store import VectorStoreManager
    
    settings = get_settings()
    
    print(f"🔍 Checking Qdrant configuration...")
    print(f"   Mode: {settings.QDRANT_MODE}")
    print(f"   URL: {settings.QDRANT_URL or 'NOT SET'}")
    print(f"   API Key: {'SET' if settings.QDRANT_API_KEY else 'NOT SET'}")
    
    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        print("❌ QDRANT_URL and QDRANT_API_KEY must be set for cloud mode")
        return False
    
    try:
        print("\n🔄 Initializing Vector Store Manager...")
        vector_store_manager = VectorStoreManager()
        
        print("✅ Successfully connected to Qdrant Cloud!")
        
        # List collections
        collections = vector_store_manager.client.get_collections()
        print(f"\n📚 Collections in cloud instance:")
        for collection in collections.collections:
            print(f"   - {collection.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant Cloud: {e}")
        return False

if __name__ == "__main__":
    success = test_qdrant_connection()
    sys.exit(0 if success else 1)