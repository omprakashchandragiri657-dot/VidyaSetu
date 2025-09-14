"""
Simple test script to verify API endpoints
Run this after setting up the database and sample data
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_colleges():
    """Test colleges endpoint"""
    print("Testing colleges endpoint...")
    response = requests.get(f"{BASE_URL}/colleges/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        colleges = response.json()
        print(f"Found {len(colleges)} colleges")
        for college in colleges:
            print(f"  - {college['name']} ({college['code']})")
    print()

def test_user_registration():
    """Test user registration"""
    print("Testing user registration...")
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "college_id": 1,
        "is_student": True
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("User registered successfully")
    else:
        print(f"Error: {response.text}")
    print()

def test_login():
    """Test user login"""
    print("Testing user login...")
    data = {
        "email": "student@example.com",
        "password": "student123"
    }
    response = requests.post(f"{BASE_URL}/token/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print("Login successful")
        return tokens['access']
    else:
        print(f"Error: {response.text}")
        return None

def test_user_details(token):
    """Test user details endpoint"""
    if not token:
        return
    
    print("Testing user details...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/me/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"User: {user['first_name']} {user['last_name']} ({user['email']})")
        print(f"College: {user['college']['name']}")
        print(f"Roles: Student={user['is_student']}, Faculty={user['is_faculty']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_achievements(token):
    """Test achievements endpoint"""
    if not token:
        return
    
    print("Testing achievements endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/achievements/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        achievements = response.json()
        print(f"Found {len(achievements)} achievements")
        for achievement in achievements:
            print(f"  - {achievement['title']} ({achievement['status']})")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("Smart Student Hub API Tests")
    print("=" * 40)
    
    try:
        test_colleges()
        test_user_registration()
        token = test_login()
        test_user_details(token)
        test_achievements(token)
        
        print("Tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
