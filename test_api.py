"""Test script for authentication and billing systems."""

import requests
import json


BASE_URL = "http://localhost:8000/api/v1"


def test_auth_signup():
    """Test user signup."""
    print("\n1️⃣  Testing Signup...")
    
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={
            "email": "test@ponsauto.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "dealership_name": "Test Motors"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["access_token"]
    return None


def test_auth_login():
    """Test user login."""
    print("\n2️⃣  Testing Login...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "test@ponsauto.com",
            "password": "testpassword123"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_get_user(token):
    """Test getting current user."""
    print("\n3️⃣  Testing Get Current User...")
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_list_plans():
    """Test listing subscription plans."""
    print("\n4️⃣  Testing List Plans...")
    
    response = requests.get(f"{BASE_URL}/billing/plans")
    
    print(f"Status: {response.status_code}")
    plans = response.json()
    
    for plan in plans:
        print(f"\n  {plan['name']} - ${plan['price']}/month")
        print(f"  Features: {', '.join(plan['features'][:3])}...")


def test_get_subscription(token):
    """Test getting user subscription."""
    print("\n5️⃣  Testing Get Subscription...")
    
    response = requests.get(
        f"{BASE_URL}/billing/subscription",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_check_limit(token, feature="vehicles_per_month"):
    """Test checking usage limits."""
    print(f"\n6️⃣  Testing Check Limit ({feature})...")
    
    response = requests.post(
        f"{BASE_URL}/billing/check-limit",
        headers={"Authorization": f"Bearer {token}"},
        json={"feature": feature}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_usage(token):
    """Test getting usage stats."""
    print("\n7️⃣  Testing Get Usage Stats...")
    
    response = requests.get(
        f"{BASE_URL}/billing/usage",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_ai_description(token):
    """Test AI description generation."""
    print("\n8️⃣  Testing AI Description...")
    
    response = requests.post(
        f"{BASE_URL}/ai/description",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "year": 2023,
            "make": "Honda",
            "model": "Accord",
            "trim": "Sport",
            "mileage": 15000,
            "price": 28500
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nTitle: {data.get('title')}")
        print(f"SEO Score: {data.get('seo_score')}/100")
        print(f"Keywords: {len(data.get('keywords', []))}")
        print(f"Hashtags: {len(data.get('hashtags', []))}")
    else:
        print(f"Response: {response.text}")


if __name__ == "__main__":
    print("🚗 PONS AUTO - API Test Suite")
    print("=" * 50)
    
    # Test authentication
    token = test_auth_signup()
    
    if not token:
        print("\n⚠️  Signup failed, trying login...")
        token = test_auth_login()
    
    if token:
        print(f"\n✅ Got access token: {token[:20]}...")
        
        # Test authenticated endpoints
        test_get_user(token)
        test_list_plans()
        test_get_subscription(token)
        test_check_limit(token)
        test_get_usage(token)
        test_ai_description(token)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n💡 Next steps:")
        print("   1. Start the backend: cd src && uvicorn shiftly.main:app --reload")
        print("   2. Run this test: python test_api.py")
        print("   3. Check results above")
        print("   4. Deploy to Railway when ready!")
    else:
        print("\n❌ Authentication failed!")
        print("\n💡 Make sure backend is running:")
        print("   cd /Users/brandonsandoval/Downloads/shiftly-auto")
        print("   source .venv/bin/activate")
        print("   uvicorn shiftly.main:app --reload")
