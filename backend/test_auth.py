"""
Authentication System Test Script

This script tests all authentication endpoints to verify the system works correctly.
Run this after starting the backend server.

Usage:
    python test_auth.py
"""

import requests
import json
import time
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"

class AuthTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_data: Optional[Dict] = None

    def print_success(self, message: str):
        print(f"✅ {message}")

    def print_error(self, message: str):
        print(f"❌ {message}")

    def print_info(self, message: str):
        print(f"ℹ️  {message}")

    def test_health(self):
        """Test health endpoint"""
        print("\n" + "="*50)
        print("Testing Health Endpoint")
        print("="*50)

        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.print_success("Health check passed")
                print(f"Response: {response.json()}")
            else:
                self.print_error(f"Health check failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Health check error: {e}")

    def test_register(self, email: str = "test@adminory.dev",
                     password: str = "testpassword123",
                     name: str = "Test User"):
        """Test user registration"""
        print("\n" + "="*50)
        print("Testing User Registration")
        print("="*50)

        payload = {
            "email": email,
            "password": password,
            "name": name
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=payload
            )

            if response.status_code == 201:
                self.print_success("User registered successfully")
                print(f"Response: {response.json()}")
                return True
            elif response.status_code == 400:
                self.print_info("User already exists (this is OK for testing)")
                return True
            else:
                self.print_error(f"Registration failed: {response.status_code}")
                print(f"Response: {response.json()}")
                return False
        except Exception as e:
            self.print_error(f"Registration error: {e}")
            return False

    def test_login(self, email: str = "test@adminory.dev",
                   password: str = "testpassword123"):
        """Test user login"""
        print("\n" + "="*50)
        print("Testing User Login")
        print("="*50)

        payload = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.user_data = data.get("user")

                self.print_success("Login successful")
                print(f"User ID: {self.user_data.get('id')}")
                print(f"Email: {self.user_data.get('email')}")
                print(f"Role: {self.user_data.get('role')}")
                print(f"Access Token: {self.access_token[:50]}...")
                return True
            else:
                self.print_error(f"Login failed: {response.status_code}")
                print(f"Response: {response.json()}")
                return False
        except Exception as e:
            self.print_error(f"Login error: {e}")
            return False

    def test_get_current_user(self):
        """Test getting current user info"""
        print("\n" + "="*50)
        print("Testing Get Current User")
        print("="*50)

        if not self.access_token:
            self.print_error("No access token available")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers=headers
            )

            if response.status_code == 200:
                user = response.json()
                self.print_success("Retrieved current user")
                print(f"User: {json.dumps(user, indent=2)}")
                return True
            else:
                self.print_error(f"Get current user failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Get current user error: {e}")
            return False

    def test_refresh_token(self):
        """Test token refresh"""
        print("\n" + "="*50)
        print("Testing Token Refresh")
        print("="*50)

        if not self.refresh_token:
            self.print_error("No refresh token available")
            return False

        payload = {"refresh_token": self.refresh_token}

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/refresh",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                old_access = self.access_token
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")

                self.print_success("Token refreshed successfully")
                print(f"New Access Token: {self.access_token[:50]}...")
                print(f"Tokens changed: {old_access != self.access_token}")
                return True
            else:
                self.print_error(f"Token refresh failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Token refresh error: {e}")
            return False

    def test_protected_endpoint(self):
        """Test accessing protected endpoint"""
        print("\n" + "="*50)
        print("Testing Protected Endpoint Access")
        print("="*50)

        # Test without token
        self.print_info("Testing without authentication...")
        response = requests.get(f"{self.base_url}/api/auth/me")
        if response.status_code == 401:
            self.print_success("Correctly rejected unauthenticated request")
        else:
            self.print_error("Should have rejected unauthenticated request")

        # Test with token
        if self.access_token:
            self.print_info("Testing with authentication...")
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers=headers
            )
            if response.status_code == 200:
                self.print_success("Correctly allowed authenticated request")
            else:
                self.print_error("Should have allowed authenticated request")

    def test_logout(self):
        """Test user logout"""
        print("\n" + "="*50)
        print("Testing User Logout")
        print("="*50)

        if not self.access_token or not self.refresh_token:
            self.print_error("No tokens available for logout")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/logout",
                headers=headers,
                params={"refresh_token": self.refresh_token}
            )

            if response.status_code == 200:
                self.print_success("Logout successful")

                # Try to use the old token
                self.print_info("Verifying token was revoked...")
                time.sleep(1)  # Give Redis a moment

                refresh_response = requests.post(
                    f"{self.base_url}/api/auth/refresh",
                    json={"refresh_token": self.refresh_token}
                )

                if refresh_response.status_code == 401:
                    self.print_success("Token correctly revoked")
                else:
                    self.print_error("Token should have been revoked")

                return True
            else:
                self.print_error(f"Logout failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Logout error: {e}")
            return False

    def run_all_tests(self):
        """Run all authentication tests"""
        print("\n" + "🚀 " * 25)
        print("Adminory Authentication System Test")
        print("🚀 " * 25)

        # Test health
        self.test_health()

        # Test registration
        self.test_register()

        # Test login
        if not self.test_login():
            print("\n❌ Login failed, cannot continue tests")
            return

        # Test getting current user
        self.test_get_current_user()

        # Test protected endpoint access
        self.test_protected_endpoint()

        # Test token refresh
        self.test_refresh_token()

        # Test logout
        self.test_logout()

        # Summary
        print("\n" + "="*50)
        print("Test Summary")
        print("="*50)
        print("✅ All authentication flows tested!")
        print("\nNext steps:")
        print("1. Test the frontend at http://localhost:3000")
        print("2. Register a new user through the UI")
        print("3. Test login and dashboard access")
        print("4. Try protected routes with different roles")


if __name__ == "__main__":
    print("Starting authentication tests...")
    print(f"Backend URL: {BASE_URL}")
    print("\nMake sure the backend is running:")
    print("  docker-compose up -d")
    print("  OR")
    print("  uvicorn app.main:app --reload")
    print("")

    input("Press Enter to continue...")

    tester = AuthTester()
    tester.run_all_tests()
