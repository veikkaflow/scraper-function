#!/usr/bin/env python
"""
Test script for the simple scraper function
Run this to test the scrape_website_data function locally
"""
import sys
import os
import json

# Add the current directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Firebase Admin (may fail locally, but that's OK for testing)
try:
    from firebase_admin import initialize_app
    try:
        initialize_app()
    except ValueError:
        # Already initialized, that's OK
        pass
except Exception as e:
    print(f"Warning: Could not initialize Firebase Admin: {e}")
    print("This is OK if you're just testing scrape_website_data function")

# Import the scrape function
from main import scrape_website_data

def test_scraper(url):
    """Test the scraper with a given URL"""
    print(f"\n{'='*60}")
    print(f"Testing scraper with URL: {url}")
    print(f"{'='*60}\n")
    
    try:
        result = scrape_website_data(url)
        
        print(f"\n{'='*60}")
        print("RESULT:")
        print(f"{'='*60}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        # Check if we got data
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            return False
        elif 'title' in result and 'text' in result:
            print(f"✅ SUCCESS!")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"Text length: {len(result.get('text', ''))} characters")
            print(f"Logos found: {len(result.get('logos', []))}")
            print(f"Colors found: {len(result.get('colors', []))}")
            return True
        else:
            print(f"⚠️  Unexpected result format")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Test URLs
    test_urls = [
        "https://www.sissipuukko.fi/",
        "https://example.com",
    ]
    
    # Use first URL from command line if provided
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    print("Simple Scraper Test Script")
    print("=" * 60)
    
    success_count = 0
    for url in test_urls:
        if test_scraper(url):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Tests completed: {success_count}/{len(test_urls)} successful")
    print(f"{'='*60}\n")

