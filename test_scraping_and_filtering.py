#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Scraping and URL Filtering
এই script দিয়ে scraping আর URL filtering test করতে পারবেন
"""

import sys
import os
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.tools.scraper import WebScraper
from backend.tools.url_filter import URLFilter
from backend.config import Config

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_success(text):
    print(f"✅ [SUCCESS] {text}")

def print_error(text):
    print(f"❌ [ERROR] {text}")

def print_info(text):
    print(f"ℹ️  [INFO] {text}")

def print_warning(text):
    print(f"⚠️  [WARNING] {text}")


def test_url_filter():
    """Test 1: URL Filtering"""
    print_header("TEST 1: URL Filtering")
    
    try:
        # Initialize URL filter
        url_filter = URLFilter()
        print_info(f"Initialized URLFilter with {len(url_filter.official_domains)} official domains")
        print_info(f"Official domains: {url_filter.official_domains}")
        
        # Test URLs - Real verified DUET links
        test_urls = [
            {"url": "https://www.duet.ac.bd/admission", "title": "Admission", "expected": True},
            {"url": "https://www.duet.ac.bd/notice/all-notices", "title": "All Notices", "expected": True},
            {"url": "https://www.duet.ac.bd/department/cse", "title": "CSE Department", "expected": True},
            {"url": "https://www.google.com", "title": "Google", "expected": False},
            {"url": "https://www.duet.ac.bd/document.pdf", "title": "PDF File", "expected": False},
        ]
        
        print_info(f"Testing {len(test_urls)} URLs...")
        
        passed = 0
        failed = 0
        
        for test in test_urls:
            url = test["url"]
            expected = test["expected"]
            
            # Test official domain check
            is_official = url_filter.is_official_url(url)
            is_valid_content = url_filter.is_valid_content_type(url)
            is_allowed = is_official and is_valid_content
            
            result_str = "✓ PASS" if is_allowed == expected else "✗ FAIL"
            
            if is_allowed == expected:
                passed += 1
                print_success(f"{result_str}: {url}")
                print(f"    → Official: {is_official}, Valid Content: {is_valid_content}")
            else:
                failed += 1
                print_error(f"{result_str}: {url}")
                print(f"    → Expected: {expected}, Got: {is_allowed}")
        
        print(f"\n📊 URL Filter Results: {passed} passed, {failed} failed out of {len(test_urls)}")
        
        return passed == len(test_urls)
        
    except Exception as e:
        print_error(f"URL Filter test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_web_scraper():
    """Test 2: Web Scraping"""
    print_header("TEST 2: Web Scraping")
    
    try:
        # Initialize scraper
        scraper = WebScraper()
        print_info("Initialized WebScraper")
        print_info(f"Timeout: {scraper.timeout}s, Max Length: {scraper.max_length} chars")
        
        # Test URL - Real verified working DUET page
        test_url = "https://www.duet.ac.bd/notice/all-notices"
        
        print_info(f"Testing scraping: {test_url}")
        print_info("This may take 5-10 seconds...")
        
        result = scraper.scrape_url(test_url)
        
        if result:
            print_success("Scraping successful!")
            print(f"\n📄 Scraped Data:")
            print(f"   - URL: {result['url']}")
            print(f"   - Title: {result['title']}")
            print(f"   - Date: {result['date'] or 'Not found'}")
            print(f"   - Content Length: {len(result['content'])} characters")
            print(f"\n📝 Content Preview (first 300 chars):")
            print("   " + "-" * 70)
            print(f"   {result['content'][:300]}...")
            print("   " + "-" * 70)
            
            return True
        else:
            print_error("Scraping failed - No content returned")
            return False
            
    except Exception as e:
        print_error(f"Web scraper test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_and_scrape():
    """Test 3: Combined Filter + Scrape"""
    print_header("TEST 3: Combined Filtering + Scraping")
    
    try:
        # Initialize both
        url_filter = URLFilter()
        scraper = WebScraper()
        
        print_info("Testing combined workflow...")
        
        # Test search results (simulated) - Using REAL verified working DUET URLs
        search_results = [
            {"url": "https://www.duet.ac.bd/admission", "title": "Admission", "snippet": "Admission info"},
            {"url": "https://www.duet.ac.bd/notice/all-notices", "title": "All Notices", "snippet": "University notices"},
            {"url": "https://www.duet.ac.bd/department/cse", "title": "CSE Department", "snippet": "CSE info"},
            {"url": "https://www.google.com/search", "title": "Google", "snippet": "Search engine"},
            {"url": "https://www.duet.ac.bd/document.pdf", "title": "PDF", "snippet": "Document"},
        ]
        
        print_info(f"Input: {len(search_results)} URLs")
        
        # Step 1: Filter URLs
        filtered_results = url_filter.filter_search_results(search_results)
        print_success(f"Filtered down to {len(filtered_results)} valid URLs")
        
        # Step 2: Scrape filtered URLs
        scraped_data = []
        for result in filtered_results:
            url = result['url']
            print_info(f"Scraping: {url}")
            
            scraped = scraper.scrape_url(url)
            if scraped:
                scraped_data.append(scraped)
                print_success(f"  ✓ Scraped: {scraped['title']} ({len(scraped['content'])} chars)")
            else:
                print_warning(f"  ✗ Failed to scrape: {url}")
        
        print(f"\n📊 Scraping Results: {len(scraped_data)} pages scraped successfully")
        
        return len(scraped_data) > 0
        
    except Exception as e:
        print_error(f"Combined test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_store_scraped_data():
    """Test 4: Store Scraped Data"""
    print_header("TEST 4: Store Scraped Data to File")
    
    try:
        # Initialize
        url_filter = URLFilter()
        scraper = WebScraper()
        
        # Real verified working DUET URLs to scrape and store
        urls_to_scrape = [
            "https://www.duet.ac.bd/notice/all-notices",
            "https://www.duet.ac.bd/admission",
            "https://www.duet.ac.bd/department/cse",
        ]
        
        print_info(f"Scraping and storing {len(urls_to_scrape)} URLs...")
        
        all_scraped_data = []
        
        for url in urls_to_scrape:
            # Filter check
            if not url_filter.is_official_url(url):
                print_warning(f"Skipping non-official URL: {url}")
                continue
            
            print_info(f"Scraping: {url}")
            result = scraper.scrape_url(url)
            
            if result:
                all_scraped_data.append(result)
                print_success(f"  ✓ Scraped: {result['title']}")
            else:
                print_error(f"  ✗ Failed to scrape: {url}")
        
        # Create output directory
        output_dir = Path("scraped_data")
        output_dir.mkdir(exist_ok=True)
        
        # Save to JSON file
        output_file = output_dir / "scraped_content.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_scraped_data, f, ensure_ascii=False, indent=2)
        
        print_success(f"Saved {len(all_scraped_data)} pages to: {output_file}")
        
        # Save to text file (human-readable)
        text_file = output_dir / "scraped_content.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            for idx, data in enumerate(all_scraped_data, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"PAGE {idx}\n")
                f.write(f"{'='*80}\n")
                f.write(f"URL: {data['url']}\n")
                f.write(f"Title: {data['title']}\n")
                f.write(f"Date: {data['date']}\n")
                f.write(f"\nContent:\n{'-'*80}\n")
                f.write(data['content'])
                f.write(f"\n{'-'*80}\n\n")
        
        print_success(f"Saved text version to: {text_file}")
        
        # Verify files exist
        if output_file.exists() and text_file.exists():
            print_success(f"✅ Both files created successfully!")
            print_info(f"   JSON: {output_file.stat().st_size} bytes")
            print_info(f"   TXT:  {text_file.stat().st_size} bytes")
            return True
        else:
            print_error("Files were not created properly")
            return False
            
    except Exception as e:
        print_error(f"Storage test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print_header("🧪 SCRAPING & URL FILTERING TEST SUITE")
    print_info("Testing web scraping and URL filtering functionality")
    print_info("Make sure you have internet connection!\n")
    
    results = {}
    
    # Test 1: URL Filtering
    results['url_filter'] = test_url_filter()
    
    # Test 2: Web Scraping
    results['scraper'] = test_web_scraper()
    
    # Test 3: Combined
    results['combined'] = test_filter_and_scrape()
    
    # Test 4: Store Data
    results['storage'] = test_store_scraped_data()
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Total: {total_tests} tests")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"{'='*80}\n")
    
    if passed_tests == total_tests:
        print_success("🎉 All tests passed! Scraping and filtering working correctly!")
        print_info("Check 'scraped_data' folder for saved content")
    else:
        print_warning(f"⚠️  {failed_tests} test(s) failed. Please check the errors above.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
