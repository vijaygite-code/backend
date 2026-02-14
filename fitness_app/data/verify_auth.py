import asyncio
import httpx
from fitness_app.main import app
from httpx import ASGITransport

async def verify_auth_fix():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        # 1. Test Register
        print("1. Testing Registration...")
        email = "newuser@test.com"
        try:
             # Cleanup if exists
             # In a real test we'd use a test DB, here we might fail if exists, that's fine.
             response = await client.post("/auth/register", json={"email": email, "password": "password123", "role": "unpaid"})
             if response.status_code == 200:
                 print("   SUCCESS: Registration worked.")
             elif response.status_code == 400 and "already registered" in response.text:
                 print("   SUCCESS: Registration endpoint reachable (User already exists).")
             else:
                 print(f"   FAILURE: {response.status_code} - {response.text}")
        except Exception as e:
             print(f"   FAILURE: {e}")

        # 2. Test Forgot Password (Non-existent user)
        print("\n2. Testing Forgot Password (Non-existent User)...")
        try:
             response = await client.post("/auth/forgot-password", json={"email": "nonexistent@void.com"})
             print(f"   Response: {response.json()}")
             # We can't easily check if email was sent here without mocking email_utils, 
             # but we verified the source code: `if not user: return`.
             if response.status_code == 200:
                 print("   SUCCESS: Returns 200 (Security Best Practice).")
             else:
                 print(f"   FAILURE: {response.status_code}")
        except Exception as e:
             print(f"   FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(verify_auth_fix())
