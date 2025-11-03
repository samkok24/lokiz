#!/usr/bin/env python3
"""
LOKIZ Backend API Integration Test
Tests critical API endpoints and workflows
"""

import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8001"
API_PREFIX = "/v1"

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def log_test(name, passed, message=""):
    """Log test result"""
    if passed:
        results["passed"].append(name)
        print(f"✅ {name}")
    else:
        results["failed"].append(f"{name}: {message}")
        print(f"❌ {name}: {message}")


def log_warning(name, message):
    """Log warning"""
    results["warnings"].append(f"{name}: {message}")
    print(f"⚠️  {name}: {message}")


# Test 1: Health Check
def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        log_test("Health Check", response.status_code == 200, 
                 f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False


# Test 2: User Registration
def test_register():
    """Test user registration"""
    try:
        username = f"testuser_{uuid4().hex[:8]}"
        payload = {
            "username": username,
            "email": f"{username}@test.com",
            "password": "Test123!@#"
        }
        response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            log_test("User Registration", "access_token" in data)
            return data.get("access_token")
        else:
            log_test("User Registration", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("User Registration", False, str(e))
        return None


# Test 3: User Login
def test_login(email="admin@lokiz.com", password="admin123"):
    """Test user login"""
    try:
        payload = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            log_test("User Login", "access_token" in data)
            return data.get("access_token")
        else:
            log_test("User Login", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("User Login", False, str(e))
        return None


# Test 4: Get Current User
def test_get_me(token):
    """Test get current user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{API_PREFIX}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Get Current User", "id" in data and "username" in data)
            return data
        else:
            log_test("Get Current User", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Current User", False, str(e))
        return None


# Test 5: Get Video Feed (Public Access)
def test_video_feed_public():
    """Test video feed without authentication"""
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/videos/")
        
        if response.status_code == 200:
            data = response.json()
            log_test("Video Feed (Public)", "videos" in data)
            return data
        else:
            log_test("Video Feed (Public)", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Video Feed (Public)", False, str(e))
        return None


# Test 6: Get Video Feed (Authenticated)
def test_video_feed_auth(token):
    """Test video feed with authentication"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{API_PREFIX}/videos/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Video Feed (Authenticated)", "videos" in data)
            return data
        else:
            log_test("Video Feed (Authenticated)", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Video Feed (Authenticated)", False, str(e))
        return None


# Test 7: Search Users (Public)
def test_search_users():
    """Test user search without authentication"""
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/search/users?q=admin")
        
        if response.status_code == 200:
            data = response.json()
            log_test("Search Users (Public)", "users" in data)
            return data
        else:
            log_test("Search Users (Public)", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Search Users (Public)", False, str(e))
        return None


# Test 8: Get Trending Hashtags
def test_trending_hashtags():
    """Test trending hashtags endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/hashtags/trending")
        
        if response.status_code == 200:
            data = response.json()
            log_test("Trending Hashtags", "hashtags" in data)
            return data
        else:
            log_test("Trending Hashtags", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Trending Hashtags", False, str(e))
        return None


# Test 9: Get User Profile (Public)
def test_user_profile():
    """Test user profile endpoint"""
    try:
        # Try to get first user from search
        search_result = test_search_users()
        if search_result and search_result.get("users"):
            user_id = search_result["users"][0]["id"]
            response = requests.get(f"{BASE_URL}{API_PREFIX}/users/{user_id}")
            
            if response.status_code == 200:
                data = response.json()
                has_stats = all(k in data for k in ["follower_count", "following_count", "video_count", "total_likes"])
                log_test("User Profile (Public)", has_stats)
                return data
            else:
                log_test("User Profile (Public)", False, f"Status: {response.status_code}")
                return None
        else:
            log_warning("User Profile (Public)", "No users found to test")
            return None
    except Exception as e:
        log_test("User Profile (Public)", False, str(e))
        return None


# Test 10: Get Notifications (Authenticated)
def test_notifications(token):
    """Test notifications endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Get Notifications", "notifications" in data)
            return data
        else:
            log_test("Get Notifications", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Notifications", False, str(e))
        return None


# Test 11: Get Unread Notification Count
def test_unread_count(token):
    """Test unread notification count"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications/unread-count", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Unread Notification Count", "unread_count" in data)
            return data
        else:
            log_test("Unread Notification Count", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Unread Notification Count", False, str(e))
        return None


# Test 12: OpenAPI Schema Validation
def test_openapi_schema():
    """Test OpenAPI schema endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        
        if response.status_code == 200:
            data = response.json()
            has_required = all(k in data for k in ["openapi", "info", "paths"])
            endpoint_count = len(data.get("paths", {}))
            log_test("OpenAPI Schema", has_required and endpoint_count > 0, 
                     f"Endpoints: {endpoint_count}")
            return data
        else:
            log_test("OpenAPI Schema", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("OpenAPI Schema", False, str(e))
        return None


def main():
    """Run all tests"""
    print("=" * 60)
    print("LOKIZ Backend API Integration Test")
    print("=" * 60)
    print()
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ Server is not healthy. Aborting tests.")
        return
    
    print()
    
    # Test 2-4: Authentication Flow
    print("--- Authentication Tests ---")
    token = test_login()
    if token:
        user = test_get_me(token)
    else:
        # Try to register new user
        token = test_register()
        if token:
            user = test_get_me(token)
    
    print()
    
    # Test 5-9: Public Access Tests
    print("--- Public Access Tests ---")
    test_video_feed_public()
    test_search_users()
    test_trending_hashtags()
    test_user_profile()
    
    print()
    
    # Test 10-11: Authenticated Tests
    if token:
        print("--- Authenticated Tests ---")
        test_video_feed_auth(token)
        test_notifications(token)
        test_unread_count(token)
    else:
        log_warning("Authenticated Tests", "No valid token, skipping authenticated tests")
    
    print()
    
    # Test 12: OpenAPI Schema
    print("--- API Documentation Tests ---")
    test_openapi_schema()
    
    # Print Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    
    if results["failed"]:
        print("\nFailed Tests:")
        for failure in results["failed"]:
            print(f"  - {failure}")
    
    if results["warnings"]:
        print("\nWarnings:")
        for warning in results["warnings"]:
            print(f"  - {warning}")
    
    print()
    
    # Exit code
    exit_code = 0 if len(results["failed"]) == 0 else 1
    return exit_code


if __name__ == "__main__":
    exit(main())

