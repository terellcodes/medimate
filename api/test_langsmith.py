#!/usr/bin/env python3
"""
Test script to verify LangSmith tracing integration.
"""
import os
from config.settings import get_settings

def test_langsmith_configuration():
    """Test LangSmith configuration."""
    print("🧪 Testing LangSmith Configuration for Vera\n")
    
    # Get settings
    settings = get_settings()
    
    print("📋 Current LangSmith Settings:")
    print(f"  LANGCHAIN_TRACING_V2: {settings.LANGCHAIN_TRACING_V2}")
    print(f"  LANGCHAIN_PROJECT: {settings.LANGCHAIN_PROJECT}")
    print(f"  LANGSMITH_API_KEY: {'***' + settings.LANGSMITH_API_KEY[-4:] if len(settings.LANGSMITH_API_KEY) > 4 else 'Not set'}")
    
    # Check environment variables after configuration
    from main import configure_langsmith
    configure_langsmith()
    
    print("\n🔧 Environment Variables After Configuration:")
    print(f"  LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2', 'Not set')}")
    print(f"  LANGCHAIN_PROJECT: {os.environ.get('LANGCHAIN_PROJECT', 'Not set')}")
    print(f"  LANGSMITH_API_KEY: {'Set' if os.environ.get('LANGSMITH_API_KEY') else 'Not set'}")
    
    # Test if tracing would be enabled
    tracing_enabled = settings.LANGCHAIN_TRACING_V2.lower() == "true" and bool(settings.LANGSMITH_API_KEY)
    
    print(f"\n🎯 LangSmith Status:")
    if tracing_enabled:
        print("  ✅ LangSmith tracing is configured and ready")
        print(f"  📊 Traces will be sent to project: {settings.LANGCHAIN_PROJECT}")
    elif settings.LANGCHAIN_TRACING_V2.lower() == "true":
        print("  ⚠️  Tracing enabled but API key missing")
        print("  💡 Add LANGSMITH_API_KEY to .env to enable tracing")
    else:
        print("  📝 LangSmith tracing is disabled")
        print("  💡 Set LANGCHAIN_TRACING_V2=true in .env to enable")
    
    return tracing_enabled

def test_langchain_integration():
    """Test that LangChain can use the tracing configuration."""
    print("\n🔗 Testing LangChain Integration...")
    
    try:
        from langchain_openai import ChatOpenAI
        from config.settings import get_settings
        
        settings = get_settings()
        
        # Create a simple LLM instance (this should pick up tracing automatically)
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        print("  ✅ LangChain OpenAI integration ready")
        print("  📡 LLM calls will be automatically traced if LangSmith is enabled")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LangChain integration error: {str(e)}")
        return False

if __name__ == "__main__":
    config_ok = test_langsmith_configuration()
    integration_ok = test_langchain_integration()
    
    print("\n" + "="*50)
    if config_ok and integration_ok:
        print("🎉 LangSmith integration is ready!")
        print("\n📝 Next steps:")
        print("  1. Add your LANGSMITH_API_KEY to .env")
        print("  2. Set LANGCHAIN_TRACING_V2=true in .env")
        print("  3. Restart the API server")
        print("  4. Check https://smith.langchain.com for traces")
    else:
        print("⚠️  LangSmith configuration needs attention")
        print("   Check the messages above for specific issues")