import asyncio
import os
import sys

# Adjust the import path if necessary.
# If test.py is in the same directory as ai_services.py,
# 'from ai_services import get_nutrition_tip' should work.
# If running from a different directory, you might need to adjust sys.path.
try:
    from ai_services import get_nutrition_tip
except ImportError:
    # Fallback for different execution contexts, e.g., if fitness_app is a package
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from fitness_app.ai_services import get_nutrition_tip


# Mock User class for testing, mimicking the structure expected by ai_services
class MockUser:
    def __init__(self, age, weight, goals):
        self.age = age
        self.weight = weight
        self.goals = goals
        # Add other attributes if they become necessary for other AI functions
        self.habit_entries = [] # Required by get_chat_response, though not by get_nutrition_tip

async def test_ai_credentials():
    print("Starting AI credentials test...")

    # Create a mock user with some sample data
    user = MockUser(age=30, weight=70, goals="lose weight and build muscle")

    print("Attempting to get a nutrition tip from the AI service...")
    try:
        # Call one of the AI service functions that uses the Gemini API
        tip = await get_nutrition_tip(user)

        print("\n--- AI Response ---")
        print(f"AI Nutrition Tip: {tip}")
        print("-------------------\n")

        # Basic check to see if the response indicates an error or a valid tip
        if "error" in tip.lower() or "trouble" in tip.lower() or "unexpected response" in tip.lower() or "sorry" in tip.lower():
            print("Result suggests an issue with AI credentials or API connectivity.")
            print("Please check the 'API_KEY' environment variable or the default key in ai_services.py.")
            print("Also, ensure there's network connectivity to the Gemini API.")
        else:
            print("AI credentials appear to be working correctly! The AI service returned a valid tip.")
            print("You can now delete this test.py file if you wish.")

    except Exception as e:
        print(f"An unexpected error occurred during the AI service call: {e}")
        print("This often indicates a problem with the API key, network, or an unhandled error in ai_services.py.")
        print("Please review the error message and your setup.")

if __name__ == "__main__":
    print("Note: The AI_API_KEY is read from the 'API_KEY' environment variable or uses a default in ai_services.py.")
    print("If you intend to test a specific key, ensure the 'API_KEY' environment variable is set before running this script.")
    asyncio.run(test_ai_credentials())
