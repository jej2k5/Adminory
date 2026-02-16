"""Test script for workspace management endpoints."""
import asyncio
import httpx
from typing import Optional, Dict, Any
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class WorkspaceTester:
    """Test workspace management functionality."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize tester."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.workspace_id: Optional[str] = None
        self.member_id: Optional[str] = None

    def print_header(self, text: str) -> None:
        """Print section header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

    def print_success(self, text: str) -> None:
        """Print success message."""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

    def print_error(self, text: str) -> None:
        """Print error message."""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

    def print_info(self, text: str) -> None:
        """Print info message."""
        print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

    def print_warning(self, text: str) -> None:
        """Print warning message."""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

    async def test_health(self) -> bool:
        """Test health endpoint."""
        self.print_header("Testing Health Endpoint")
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Health check passed: {data}")
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Health check error: {str(e)}")
            return False

    async def test_register(self, email: str, password: str, name: str) -> bool:
        """Test user registration."""
        self.print_header("Testing User Registration")
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/register",
                json={"email": email, "password": password, "name": name}
            )
            if response.status_code == 201:
                data = response.json()
                self.print_success(f"Registration successful: {data['email']}")
                return True
            elif response.status_code == 400:
                self.print_warning("User already exists (expected)")
                return True
            else:
                self.print_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Registration error: {str(e)}")
            return False

    async def test_login(self, email: str, password: str) -> bool:
        """Test user login."""
        self.print_header("Testing User Login")
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                self.user_id = data["user"]["id"]
                self.print_success(f"Login successful: {data['user']['email']}")
                self.print_info(f"User ID: {self.user_id}")
                return True
            else:
                self.print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Login error: {str(e)}")
            return False

    async def test_create_workspace(self, name: str, slug: Optional[str] = None) -> bool:
        """Test workspace creation."""
        self.print_header("Testing Workspace Creation")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            payload = {"name": name}
            if slug:
                payload["slug"] = slug

            response = await self.client.post(
                f"{self.base_url}/api/external/workspaces",
                json=payload,
                headers=headers
            )
            if response.status_code == 201:
                data = response.json()
                self.workspace_id = data["id"]
                self.print_success(f"Workspace created: {data['name']} ({data['slug']})")
                self.print_info(f"Workspace ID: {self.workspace_id}")
                self.print_info(f"Plan: {data['plan']}")
                self.print_info(f"Owner ID: {data['owner_id']}")
                return True
            else:
                self.print_error(f"Workspace creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Workspace creation error: {str(e)}")
            return False

    async def test_list_workspaces(self) -> bool:
        """Test listing workspaces."""
        self.print_header("Testing List Workspaces")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/external/workspaces",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Found {len(data)} workspace(s)")
                for ws in data:
                    self.print_info(f"  - {ws['name']} ({ws['slug']}) - Role: {ws.get('user_role', 'N/A')}")
                return True
            else:
                self.print_error(f"List workspaces failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"List workspaces error: {str(e)}")
            return False

    async def test_get_workspace(self) -> bool:
        """Test getting workspace details."""
        self.print_header("Testing Get Workspace Details")
        if not self.workspace_id:
            self.print_warning("No workspace ID available, skipping test")
            return True

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/external/workspaces/{self.workspace_id}",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Workspace details retrieved: {data['name']}")
                self.print_info(f"Members: {len(data.get('members', []))}")
                self.print_info(f"SSO Enabled: {data['sso_enabled']}")
                self.print_info(f"Created: {data['created_at']}")
                return True
            else:
                self.print_error(f"Get workspace failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Get workspace error: {str(e)}")
            return False

    async def test_update_workspace(self) -> bool:
        """Test updating workspace."""
        self.print_header("Testing Update Workspace")
        if not self.workspace_id:
            self.print_warning("No workspace ID available, skipping test")
            return True

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            new_name = f"Updated Workspace {datetime.now().strftime('%H:%M:%S')}"
            response = await self.client.patch(
                f"{self.base_url}/api/external/workspaces/{self.workspace_id}",
                json={"name": new_name},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Workspace updated: {data['name']}")
                return True
            else:
                self.print_error(f"Update workspace failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Update workspace error: {str(e)}")
            return False

    async def test_list_members(self) -> bool:
        """Test listing workspace members."""
        self.print_header("Testing List Workspace Members")
        if not self.workspace_id:
            self.print_warning("No workspace ID available, skipping test")
            return True

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/external/workspaces/{self.workspace_id}/members",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Found {len(data)} member(s)")
                for member in data:
                    self.print_info(f"  - User {member['user_id'][:8]}... - Role: {member['role']}")
                    if member['role'] == 'owner':
                        self.member_id = member['id']
                return True
            else:
                self.print_error(f"List members failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"List members error: {str(e)}")
            return False

    async def test_workspace_by_slug(self, slug: str) -> bool:
        """Test getting workspace by slug."""
        self.print_header("Testing Get Workspace By Slug")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/external/workspaces/by-slug/{slug}",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Workspace found by slug: {data['name']} ({data['slug']})")
                return True
            else:
                self.print_error(f"Get by slug failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Get by slug error: {str(e)}")
            return False

    async def run_all_tests(self) -> None:
        """Run all tests."""
        print(f"\n{Colors.BOLD}{'=' * 60}")
        print(f"Adminory Workspace Management Test Suite")
        print(f"{'=' * 60}{Colors.ENDC}\n")

        # Unique test user
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_email = f"workspace_test_{timestamp}@example.com"
        test_password = "TestPass123!"
        test_name = "Workspace Tester"
        workspace_name = f"Test Workspace {timestamp}"
        workspace_slug = f"test-workspace-{timestamp}"

        results = []

        # Run tests in sequence
        results.append(("Health Check", await self.test_health()))
        results.append(("Register User", await self.test_register(test_email, test_password, test_name)))
        results.append(("Login", await self.test_login(test_email, test_password)))
        results.append(("Create Workspace", await self.test_create_workspace(workspace_name, workspace_slug)))
        results.append(("List Workspaces", await self.test_list_workspaces()))
        results.append(("Get Workspace", await self.test_get_workspace()))
        results.append(("Update Workspace", await self.test_update_workspace()))
        results.append(("List Members", await self.test_list_members()))
        results.append(("Get by Slug", await self.test_workspace_by_slug(workspace_slug)))

        # Print summary
        self.print_header("Test Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            if result:
                self.print_success(f"{test_name}: PASSED")
            else:
                self.print_error(f"{test_name}: FAILED")

        print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")

        if passed == total:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Some tests failed{Colors.ENDC}\n")

        await self.client.aclose()


async def main():
    """Main test runner."""
    tester = WorkspaceTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
