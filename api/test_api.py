#!/usr/bin/env python3
"""
Simple test script to verify API structure and basic functionality.
"""
import asyncio
import sys
import os

# Add the API directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all modules can be imported."""
    try:
        # Test core imports
        from core.vector_store import vector_store_manager
        print("✓ Vector store manager imported successfully")
        
        # Test services
        from services.rag_service import rag_service
        print("✓ RAG service imported successfully")
        
        from services.pdf_service import pdf_service
        print("✓ PDF service imported successfully")
        
        from services.analysis_service import analysis_service
        print("✓ Analysis service imported successfully")
        
        # Test schemas
        from models.schemas.upload import UploadResponse
        from models.schemas.analysis import AnalysisResponse
        print("✓ Schemas imported successfully")
        
        # Test routes
        from routes.upload import router as upload_router
        from routes.analysis import router as analysis_router
        print("✓ Routes imported successfully")
        
        # Test main app
        from main import app
        print("✓ FastAPI app created successfully")
        
        print("\n🎉 All imports successful! API structure is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

async def test_vector_store():
    """Test vector store initialization."""
    try:
        from core.vector_store import vector_store_manager
        
        # Test getting vector stores
        guidelines_store = vector_store_manager.get_guidelines_vector_store()
        predicate_store = vector_store_manager.get_predicate_device_vector_store()
        
        print("✓ Vector stores initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Vector store error: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🔧 Testing VeraMate API Structure\n")
    
    # Test imports
    imports_ok = await test_imports()
    
    if imports_ok:
        # Test vector store
        vector_ok = await test_vector_store()
        
        if vector_ok:
            print("\n✅ All tests passed! The API is ready for testing.")
            print("\nNext steps:")
            print("1. Set OPENAI_API_KEY in .env file")
            print("2. Start the server: uvicorn main:app --reload")
            print("3. Visit http://localhost:8000/docs for API documentation")
        else:
            print("\n⚠️  Vector store tests failed, but basic structure is OK")
    else:
        print("\n❌ Import tests failed. Please check dependencies.")

if __name__ == "__main__":
    asyncio.run(main())