import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    url = f"{BASE_URL}/api/crew/login"
    payload = {
        "id": "som",
        "password": "cauchemar123"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login Test Passed")
        else:
            print("❌ Login Test Failed")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_login()
