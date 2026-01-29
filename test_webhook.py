"""
Test script for webhook endpoint
Run this to simulate GitHub webhook events
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/webhook"

def test_push_event():
    """Test PUSH event"""
    print("\n🚀 Testing PUSH event...")
    
    payload = {
        "ref": "refs/heads/main",
        "pusher": {
            "name": "TestUser"
        },
        "head_commit": {
            "id": "abc123def456",
            "message": "Test commit",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/receiver", 
                                json=payload, 
                                headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_pull_request_event():
    """Test PULL_REQUEST event"""
    print("\n🔀 Testing PULL_REQUEST event...")
    
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 42,
            "user": {
                "login": "TestUser"
            },
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/receiver", 
                                json=payload, 
                                headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_merge_event():
    """Test MERGE event"""
    print("\n✅ Testing MERGE event...")
    
    payload = {
        "action": "closed",
        "pull_request": {
            "number": 43,
            "merged": True,
            "merged_by": {
                "login": "TestUser"
            },
            "head": {
                "ref": "dev"
            },
            "base": {
                "ref": "main"
            },
            "merged_at": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/receiver", 
                                json=payload, 
                                headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_events():
    """Test GET events endpoint"""
    print("\n📋 Testing GET events endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/events")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Events: {data.get('count', 0)}")
        
        if data.get('events'):
            print("\nRecent Events:")
            for event in data['events'][:3]:  # Show first 3
                print(f"  - {event['action']}: {event['author']} -> {event['to_branch']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print("\n💚 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("GitHub Webhook Endpoint Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("PUSH Event", test_push_event),
        ("PULL_REQUEST Event", test_pull_request_event),
        ("MERGE Event", test_merge_event),
        ("GET Events", test_get_events),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
