import httpx
import asyncio
import base64
from fitness_app.core.database import SessionLocal, engine
from fitness_app import models
from fitness_app.auth import auth

BASE_URL = "http://127.0.0.1:8000"
# Use a valid email/password from your seed data or create one
EMAIL = "test@example.com"
PASSWORD = "password123"

from fitness_app.main import app
from httpx import ASGITransport

async def verify_gym():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # 1. Login
        print("1. Logging in...")
        try:
            response = await client.post("/token", data={"username": EMAIL, "password": PASSWORD})
            if response.status_code == 401:
                 # Try creating user if login fails (first run)
                 print("   Login failed, trying to register...")
                 await client.post("/users/", json={"email": EMAIL, "password": PASSWORD, "age": 30, "weight": 70, "height": 175, "goals": "Muscle Gain"})
                 response = await client.post("/token", data={"username": EMAIL, "password": PASSWORD})
            
            response.raise_for_status()
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   Login successful.")
        except Exception as e:
            print(f"   FATAL: Login failed: {repr(e)}")
            return

        # 2. Test Habits
        print("\n2. Testing Habit Creation...")
        habit_data = {
            "date": "2023-10-27", 
            "sleep_hours": 7.5,
            "water_liters": 2.5,
            "steps": 10500,
            "daily_notes": "Feeling great!"
        }
        try:
            response = await client.post("/habits/", json=habit_data, headers=headers)
            response.raise_for_status()
            print(f"   Habit created: {response.json()['id']}")
        except Exception as e:
            print(f"   Error creating habit: {e}")

        # 3. Test Meal Log
        print("\n3. Testing Meal Log Creation...")
        meal_data = {
            "date": "2023-10-27",
            "meal_type": "Lunch",
            "description": "Chicken and Rice",
            "calories": 600,
            "protein_g": 40,
            "carbs_g": 50,
            "fats_g": 10
        }
        try:
            response = await client.post("/meals/", json=meal_data, headers=headers)
            response.raise_for_status()
            print(f"   Meal Log created: {response.json()['id']}")
        except Exception as e:
            print(f"   Error creating meal log: {e}")

        # 4. Test AI Meal Analysis (Mocked Image)
        print("\n4. Testing AI Meal Analysis...")
        # Small white pixel base64
        mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKwjwAAAAABJRU5ErkJggg=="
        try:
            response = await client.post("/ai/analyze-meal", json={"image_base64": mock_image}, headers=headers)
            if response.status_code == 200:
                print(f"   AI Response: {response.json().get('description')}")
            else:
                 print(f"   AI Request failed with {response.status_code} (Expected if API key invalid or quota exceeded)")
        except Exception as e:
            print(f"   Error calling AI endpoint: {e}")

        # 5. Test Forgot Password
        print("\n5. Testing Forgot Password...")
        try:
             # Use the email we logged in with (test@example.com) - ensure it exists in DB
             response = await client.post("/auth/forgot-password", json={"email": EMAIL})
             response.raise_for_status()
             print(f"   Forgot Password Request successful: {response.json()}")
        except Exception as e:
             print(f"   Error requesting password reset: {e}")

if __name__ == "__main__":
    asyncio.run(verify_gym())
