#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick script to verify which DUET URLs are working
"""

import requests
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def check_url(url):
    """Check if URL is accessible"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Encoding': 'gzip, deflate'  # Don't request brotli to avoid decoding issues
        }
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code, len(response.text)
    except Exception as e:
        return None, str(e)

# DUET URLs to test - More comprehensive list
test_urls = [
    # Main pages
    "https://www.duet.ac.bd",
    "https://duet.ac.bd",
    
    # Academic pages
    "https://www.duet.ac.bd/admission",
    "https://www.duet.ac.bd/departments",
    "https://www.duet.ac.bd/academics",
    "https://www.duet.ac.bd/academic-calender",
    "https://www.duet.ac.bd/about",
    "https://www.duet.ac.bd/about/history",
    
    # Department pages
    "https://www.duet.ac.bd/department/cse",
    "https://www.duet.ac.bd/department/eee",
    "https://www.duet.ac.bd/department/me",
    
    # Office pages
    "https://www.duet.ac.bd/office/central-library",
    
    # Notices and Events
    "https://www.duet.ac.bd/notice/all-notices",
    "https://www.duet.ac.bd/notice/all-noticess",  # Checking both spellings
    "https://www.duet.ac.bd/notices",
    "https://www.duet.ac.bd/events",
    
    # Other sections
    "https://www.duet.ac.bd/research",
    "https://www.duet.ac.bd/faculty",
    "https://www.duet.ac.bd/contact",
]

print("🔍 Checking DUET URLs...\n")
print("=" * 80)

working_urls = []
for url in test_urls:
    print(f"\n📍 Testing: {url}")
    status, info = check_url(url)
    
    if status:
        if 200 <= status < 300:
            print(f"   ✅ Working! (Status: {status}, Size: {info} bytes)")
            working_urls.append(url)
        elif 300 <= status < 400:
            print(f"   ⚠️  Redirect (Status: {status})")
        else:
            print(f"   ❌ Error (Status: {status})")
    else:
        print(f"   ❌ Failed: {info}")

print("\n" + "=" * 80)
print(f"\n✅ Working URLs ({len(working_urls)}):")
for url in working_urls:
    print(f"   - {url}")

print("\n💡 Use these URLs in your tests!")
