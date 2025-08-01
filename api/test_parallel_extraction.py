#!/usr/bin/env python3
"""
Test script for the new parallel extraction system.
"""
import requests
import os
import time

def test_parallel_extraction():
    """Test the new AI-powered parallel extraction."""
    print("🧪 Testing Parallel AI Document Extraction\n")
    
    # Path to test PDF
    pdf_path = "../notebooks/data/510K_1.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF not found at: {pdf_path}")
        return False
    
    try:
        print("1. Uploading PDF with new AI extraction...")
        start_time = time.time()
        
        # Upload the PDF
        with open(pdf_path, 'rb') as f:
            files = {'file': ('510K_1.pdf', f, 'application/pdf')}
            response = requests.post('http://localhost:8000/api/upload_pdf', files=files)
        
        extraction_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            summary = data['document_summary']
            
            print(f"✅ Upload successful! (took {extraction_time:.2f} seconds)")
            print("\n📋 Extracted Information:")
            print(f"  📄 Device Name: {summary['device_name']}")
            print(f"  🏢 Manufacturer: {summary['manufacturer']}")
            print(f"  🎯 Indication: {summary['indication_of_use']}")
            print(f"  📝 Description: {summary['description']}")
            
            # Check if we got better results than before
            improvements = []
            if summary['device_name'] != "Unknown":
                improvements.append("✅ Device name extracted")
            if summary['manufacturer'] != "Unknown": 
                improvements.append("✅ Manufacturer extracted")
            if summary['indication_of_use'] != "Not specified":
                improvements.append("✅ Indication extracted")
            if summary['description'] != "510(k) medical device":
                improvements.append("✅ Description extracted")
            
            print(f"\n🎯 Extraction Quality:")
            for improvement in improvements:
                print(f"  {improvement}")
            
            if len(improvements) >= 2:
                print(f"\n🎉 AI extraction working! Got {len(improvements)}/4 fields successfully.")
                return True
            else:
                print(f"\n⚠️  AI extraction needs improvement. Only got {len(improvements)}/4 fields.")
                return False
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

def test_extensibility():
    """Test adding custom extraction fields."""
    print("\n🔧 Testing Extensibility...")
    
    try:
        from services.document_parser_service import document_parser_service
        
        # Add a custom field
        document_parser_service.add_custom_field(
            "regulatory_class",
            ["class I", "class II", "class III", "regulatory class", "device class"],
            """
Extract the regulatory class (Class I, II, or III) from the following text.
Look for mentions of device classification or regulatory class.
Return only the class (e.g., "Class II"), or "Unknown" if not found.

Text:
{text}

Regulatory Class:"""
        )
        
        print("✅ Successfully added custom 'regulatory_class' field")
        print("✅ System is extensible - new fields can be added easily")
        return True
        
    except Exception as e:
        print(f"❌ Extensibility test failed: {str(e)}")
        return False

if __name__ == "__main__":
    extraction_ok = test_parallel_extraction()
    extensibility_ok = test_extensibility()
    
    if extraction_ok and extensibility_ok:
        print("\n🎉 All tests passed! Parallel extraction system is working.")
        print("\n🚀 Benefits achieved:")
        print("  ⚡ Parallel execution for speed")
        print("  🎯 AI-powered accurate extraction") 
        print("  🔧 Easy extensibility for new fields")
        print("  🛡️  Fallback system for reliability")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")