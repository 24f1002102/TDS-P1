#!/usr/bin/env python3
"""
Test the student API locally.
"""
import requests
import json
import sys

def test_student_api(endpoint: str = "http://localhost:8000"):
    """Test student API with sample request."""
    
    # Load sample request
    with open("examples/sample_task_request.json", "r") as f:
        task_request = json.load(f)
    
    print(f"Testing student API at {endpoint}")
    print(f"Task: {task_request['task']}")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{endpoint}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Send task request
    print("\n2. Sending task request...")
    try:
        response = requests.post(
            f"{endpoint}/api/task",
            json=task_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ Task accepted! Check logs for processing status.")
            print("   Generated repo should appear on GitHub shortly.")
        else:
            print(f"\n❌ Task rejected: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_student_api(endpoint)
