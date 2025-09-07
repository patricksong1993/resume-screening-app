#!/usr/bin/env python3
"""
Test script for the resume response caching system
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_cache_status():
    """Test the cache status endpoint"""
    print("🔍 Testing cache status endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cache-status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache status retrieved successfully")
            print(f"📊 Total cached responses: {data.get('total_cached_responses', 0)}")
            print(f"📊 Average match score: {data.get('average_match_score', 0)}")
            print(f"📊 Recommendations breakdown: {data.get('recommendations_breakdown', {})}")
            
            latest = data.get('latest_responses', [])
            if latest:
                print(f"📋 Latest responses:")
                for i, resp in enumerate(latest[-3:], 1):  # Show last 3
                    print(f"   {i}. {resp.get('candidate_name', 'Unknown')} - {resp.get('match_score', 0)}% - {resp.get('recommendation', 'Unknown')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing cache status: {str(e)}")

def test_mock_mode():
    """Test mock mode with cached responses"""
    print("\n🎭 Testing mock mode with cached responses...")
    
    # Create a simple test file (you would normally upload a real PDF)
    test_data = {
        'job_description': 'Software Engineer position requiring Python and React skills',
        'mock': 'true'
    }
    
    # Note: For a real test, you would need to upload an actual PDF file
    # files = {'file': ('test_resume.pdf', open('test_resume.pdf', 'rb'), 'application/pdf')}
    
    try:
        # This is just to demonstrate the endpoint - you would need a real PDF file
        print("💡 To test mock mode, use this curl command:")
        print(f"curl -X POST {BASE_URL}/api/upload-resume \\")
        print("  -F 'file=@your_test_resume.pdf' \\")
        print("  -F 'job_description=Software Engineer position' \\")
        print("  -F 'mock=true'")
        print("\n📝 This will return a random cached response instead of processing the file")
        
    except Exception as e:
        print(f"❌ Error testing mock mode: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Resume Response Cache System Test")
    print("=" * 50)
    
    # Test cache status
    test_cache_status()
    
    # Test mock mode
    test_mock_mode()
    
    print("\n" + "=" * 50)
    print("📋 Test completed!")
    print("\n💡 How the caching system works:")
    print("1. When you process resumes normally (mock=false), responses are saved to cache")
    print("2. When you use mock mode (mock=true), a random cached response is returned")
    print("3. Use /api/cache-status to see cache statistics")
    print("4. Cache is stored in: backend/app/response_cache/resume_responses.json")

if __name__ == "__main__":
    main()
