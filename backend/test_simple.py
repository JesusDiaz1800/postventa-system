#!/usr/bin/env python
import requests
import json

def test_login():
    """Test login endpoint"""
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json={
            "username": "admin",
            "password": "admin123"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Login successful!")
            print(f"User role: {data.get('user', {}).get('role')}")
            print(f"User is_admin: {data.get('user', {}).get('is_admin')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == '__main__':
    test_login()
