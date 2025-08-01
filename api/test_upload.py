#!/usr/bin/env python3
"""
Test script to verify PDF upload functionality.
"""
import requests
import os

def test_upload():
    """Test the PDF upload endpoint."""
    # Path to a test PDF
    pdf_path = "../notebooks/data/510K_1.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF not found at: {pdf_path}")
        return False
    
    try:
        # Upload the PDF
        with open(pdf_path, 'rb') as f:
            files = {'file': ('510K_1.pdf', f, 'application/pdf')}
            response = requests.post('http://localhost:8000/api/upload_pdf', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"📄 Device: {data['document_summary']['device_name']}")
            print(f"🏢 Manufacturer: {data['document_summary']['manufacturer']}")
            print(f"📋 Indication: {data['document_summary']['indication_of_use']}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload: {str(e)}")
        return False

def test_analysis():
    """Test the analysis endpoint."""
    try:
        indication = "For use in temporary occlusion of large vessels and expansion of vascular prostheses."
        
        response = requests.post(
            'http://localhost:8000/api/analyze_device',
            json={'new_device_indication': indication}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis successful!")
            if data['success']:
                result = data['analysis']
                equivalent = result['substantially_equivalent']
                print(f"🔍 Substantially Equivalent: {'YES' if equivalent else 'NO'}")
                print(f"📝 Reasons: {len(result['reasons'])} provided")
                print(f"📚 Citations: {len(result['citations'])} provided")
                return True
            else:
                print("❌ Analysis failed:", data.get('error'))
                return False
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing VeraMate API\n")
    
    print("1. Testing PDF Upload...")
    upload_ok = test_upload()
    
    if upload_ok:
        print("\n2. Testing Device Analysis...")
        analysis_ok = test_analysis()
        
        if analysis_ok:
            print("\n🎉 All tests passed! The API is working correctly.")
        else:
            print("\n⚠️  Analysis test failed, but upload works.")
    else:
        print("\n❌ Upload test failed. Check the server and try again.")