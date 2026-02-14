import asyncio
import httpx
from fitness_app.main import app
from httpx import ASGITransport

EMAIL = "test@gym.com" # Unpaid user
PASSWORD = "user123"

async def verify_profile():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # 1. Login
        print("1. Logging in...")
        try:
             response = await client.post("/auth/token", data={"username": EMAIL, "password": PASSWORD})
             response.raise_for_status()
             token = response.json()["access_token"]
             headers = {"Authorization": f"Bearer {token}"}
             print("   Login successful.")
        except Exception as e:
             print(f"   FATAL: Login failed: {e}")
             return

        # 2. Update Profile
        print("\n2. Testing Profile Update...")
        try:
             update_data = {
                 "age": 30,
                 "weight": 85.5,
                 "height": 180.0,
                 "goals": "Build muscle and endurance",
                 "profile_picture": "https://example.com/me.jpg"
             }
             response = await client.put("/users/me/", json=update_data, headers=headers)
             response.raise_for_status()
             user_data = response.json()
             print(f"   Update successful: {user_data['age']} years, {user_data['profile_picture']}")
             if user_data['profile_picture'] == "https://example.com/me.jpg":
                 print("   SUCCESS: Profile picture updated.")
             else:
                 print("   FAILURE: Profile picture mismatch.")
        except Exception as e:
             print(f"   Error updating profile: {e}")

if __name__ == "__main__":
    asyncio.run(verify_profile())
