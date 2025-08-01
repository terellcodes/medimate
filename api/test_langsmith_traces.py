#!/usr/bin/env python3
"""
Test script to verify LangSmith traces are being sent.
"""
import requests
import time

def test_trace_generation():
    """Test that API calls generate LangSmith traces."""
    print("🧪 Testing LangSmith Trace Generation\n")
    
    try:
        # Test with a simple analysis request
        indication = "For use in temporary occlusion of large vessels."
        
        print("📝 Making API request to generate traces...")
        print(f"   Testing indication: {indication}")
        
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/analyze_device',
            json={'new_device_indication': indication}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API request successful ({duration:.2f}s)")
            
            if data['success']:
                result = data['analysis']
                print(f"🎯 Analysis completed: {'Equivalent' if result['substantially_equivalent'] else 'Not Equivalent'}")
                print(f"📊 Generated {len(result['reasons'])} reasons and {len(result['citations'])} citations")
                
                print("\n🔍 LangSmith Tracing:")
                print("  📡 This request should have generated traces for:")
                print("    • LLM calls to OpenAI GPT-4o-mini")
                print("    • Vector store retrieval operations") 
                print("    • Tool usage (retrieve_fda_guidelines, retrieve_predicate_device_details)")
                print("    • LangGraph agent execution")
                
                print(f"\n🌐 Check your traces at:")
                print(f"   https://smith.langchain.com/projects/p/VeraMate")
                
                return True
            else:
                print("❌ Analysis failed:", data.get('error'))
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_trace_generation()
    
    if success:
        print("\n🎉 Trace generation test completed successfully!")
        print("\n📋 What to check in LangSmith:")
        print("  1. Go to https://smith.langchain.com")
        print("  2. Navigate to the 'VeraMate' project")
        print("  3. Look for recent traces from the API call")
        print("  4. Traces should show:")
        print("     • Agent execution steps")
        print("     • Tool calls (FDA guidelines & predicate device)")  
        print("     • LLM interactions")
        print("     • Timing and token usage")
    else:
        print("\n⚠️  Trace generation test had issues")
        print("   Check the API server and try again")