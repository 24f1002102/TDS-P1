"""
Test script to debug AI pipe connection
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
api_url = "https://aipipe.org/openai/v1/chat/completions"

print("=" * 60)
print("Testing AI Pipe Connection")
print("=" * 60)
print(f"API URL: {api_url}")
print(f"API Key (first 20 chars): {api_key[:20]}...")
print()

# Test 1: Simple request
print("Test 1: Simple message")
print("-" * 60)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Try with minimal payload first
payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "user", "content": "Say 'Hello'"}
    ]
}

print("Sending request...")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print("❌ Error!")
        print(f"Response: {response.text}")
        
        # Try to parse error as JSON
        try:
            error_json = response.json()
            print(f"\nParsed Error: {json.dumps(error_json, indent=2)}")
        except:
            pass
            
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print()

# Test 2: With different parameters
print("Test 2: With max_tokens parameter")
print("-" * 60)

payload2 = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "user", "content": "Say 'Hello'"}
    ],
    "max_tokens": 50
}

try:
    response = requests.post(
        api_url,
        headers=headers,
        json=payload2,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success with max_tokens!")
    else:
        print("❌ Failed with max_tokens")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()
print("=" * 60)
print()

# Test 3: Try without model parameter
print("Test 3: Without model parameter")
print("-" * 60)

payload3 = {
    "messages": [
        {"role": "user", "content": "Say 'Hello'"}
    ]
}

try:
    response = requests.post(
        api_url,
        headers=headers,
        json=payload3,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success without model!")
    else:
        print("❌ Failed without model")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()
print("=" * 60)