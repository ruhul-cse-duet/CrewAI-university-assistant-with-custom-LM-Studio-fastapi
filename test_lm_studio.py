#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LM Studio Connection and Response
এই script দিয়ে LM Studio connection test করতে পারবেন
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.llm import LMStudioLLM, get_llm
from backend.config import Config
import requests
import json

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def test_lm_studio_connection():
    """Test 1: Check if LM Studio server is running"""
    print_header("TEST 1: LM Studio Server Connection")
    
    try:
        base_url = Config.LM_STUDIO_BASE_URL.replace('/v1', '')
        models_url = f"{base_url}/v1/models"
        
        print_info(f"Checking: {models_url}")
        response = requests.get(models_url, timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print_success("LM Studio server is running!")
            print_info(f"Available models: {len(models.get('data', []))}")
            
            for model in models.get('data', [])[:3]:
                print(f"   - {model.get('id', 'Unknown')}")
            
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to LM Studio server")
        print_info("Make sure LM Studio is running on port 1234")
        print_info("Steps:")
        print("   1. Open LM Studio")
        print("   2. Load a model")
        print("   3. Start Local Server on port 1234")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_llm_initialization():
    """Test 2: Initialize LLM class"""
    print_header("TEST 2: LLM Class Initialization")
    
    try:
        print_info("Initializing LMStudioLLM...")
        llm = get_llm()
        
        print_success("LLM initialized successfully!")
        print_info(f"Base URL: {llm.base_url}")
        print_info(f"Model: {llm.model or 'Not set (will use default)'}")
        print_info(f"API Key: {llm.api_key}")
        
        return llm
        
    except Exception as e:
        print_error(f"Initialization failed: {str(e)}")
        return None

def test_simple_prompt(llm):
    """Test 3: Simple prompt test"""
    print_header("TEST 3: Simple Prompt Test")
    
    if not llm:
        print_error("LLM not initialized, skipping test")
        return False
    
    try:
        test_prompt = "Hello, can you hear me? Just reply with 'Yes, I can hear you.'"
        print_info(f"Sending prompt: '{test_prompt}'")
        print_info("Waiting for response (this may take 10-30 seconds)...")
        
        response = llm.invoke(test_prompt)
        
        print_success("Response received!")
        print("\n" + "-"*70)
        print("LLM Response:")
        print("-"*70)
        print(response)
        print("-"*70 + "\n")
        
        return True
        
    except Exception as e:
        print_error(f"Error getting response: {str(e)}")
        print_info("Possible issues:")
        print("   - Model not loaded in LM Studio")
        print("   - Model name mismatch in .env")
        print("   - LM Studio server not responding")
        return False

def test_bengali_prompt(llm):
    """Test 4: Bengali prompt test"""
    print_header("TEST 4: Bengali Prompt Test")
    
    if not llm:
        print_error("LLM not initialized, skipping test")
        return False
    
    try:
        test_prompt = "তুমি কি বাংলা বুঝতে পারো? শুধু 'হ্যাঁ, আমি বাংলা বুঝতে পারি' লিখো।"
        print_info(f"Sending Bengali prompt...")
        print_info("Waiting for response...")
        
        response = llm.invoke(test_prompt)
        
        print_success("Response received!")
        print("\n" + "-"*70)
        print("LLM Response (Bengali):")
        print("-"*70)
        print(response)
        print("-"*70 + "\n")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_university_query(llm):
    """Test 5: University-related query"""
    print_header("TEST 5: University Query Test")
    
    if not llm:
        print_error("LLM not initialized, skipping test")
        return False
    
    try:
        test_prompt = """You are a helpful university assistant. Answer this question:

Question: What is today's notice?

Information:
[Source 1]
Title: Exam Schedule
URL: https://duet.ac.bd/all-notice
Content: The exam schedule has been published. Exams will start from next week.

Answer the question based on the information provided."""
        
        print_info("Sending university query...")
        print_info("This simulates a real query from the system")
        print_info("Waiting for response (may take 15-30 seconds)...")
        
        response = llm.invoke(test_prompt)
        
        print_success("Response received!")
        print("\n" + "-"*70)
        print("LLM Response:")
        print("-"*70)
        print(response)
        print("-"*70 + "\n")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("LM Studio Connection Test")
    print_info("This script will test if LM Studio is working correctly")
    print_info("Make sure LM Studio is running with a model loaded\n")
    
    # Test 1: Connection
    if not test_lm_studio_connection():
        print("\n" + "="*70)
        print_error("LM Studio server is not accessible. Please fix this first.")
        print("="*70)
        return
    
    # Test 2: Initialization
    llm = test_llm_initialization()
    if not llm:
        print("\n" + "="*70)
        print_error("LLM initialization failed. Check your configuration.")
        print("="*70)
        return
    
    # Test 3: Simple prompt
    if not test_simple_prompt(llm):
        print("\n" + "="*70)
        print_error("Simple prompt test failed.")
        print("="*70)
        return
    
    # Test 4: Bengali prompt
    test_bengali_prompt(llm)
    
    # Test 5: University query
    test_university_query(llm)
    
    # Summary
    print_header("TEST SUMMARY")
    print_success("All tests completed!")
    print_info("If all tests passed, your LM Studio is working correctly.")
    print_info("You can now run the full project with: python start.py")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

