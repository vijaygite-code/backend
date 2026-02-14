import httpx
import os
import json
from typing import List, Optional
from fitness_app import schemas

# IMPORTANT: In a real application, get this from environment variables!
AI_API_KEY = os.getenv("AI_API_KEY", "")
# Using Google Gemini API endpoint
AI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={AI_API_KEY}"

async def call_gemini(prompt: str) -> str:
    if not AI_API_KEY:
        return "AI_API_KEY_MISSING"
        
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(AI_API_URL, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "AI_ERROR"

async def check_toxicity(text: str) -> tuple[bool, Optional[str]]:
    """
    Returns (is_toxic, reason)
    """
    if not AI_API_KEY:
        return False, None # Fail open if no key

    prompt = f"""
    Analyze the following text for toxicity, hate speech, bullying, or violence.
    Text: "{text}"
    
    Return a JSON object with:
    - "is_toxic": boolean
    - "reason": string (short explanation if toxic, else null)
    
    Strictly JSON only.
    """
    
    response_text = await call_gemini(prompt)
    if response_text in ["AI_API_KEY_MISSING", "AI_ERROR"]:
        return False, None
        
    try:
        # Clean markdown code blocks if present
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
        return result.get("is_toxic", False), result.get("reason")
    except:
        return False, None

async def generate_challenge_idea() -> dict:
    prompt = """
    Create a unique, exciting fitness challenge for a gym community.
    Return a JSON object with:
    - "title": string (catchy name)
    - "description": string (1-2 sentences)
    - "duration_days": integer (e.g. 30)
    - "color": string (Tailwind gradient class, e.g. "from-blue-500 to-purple-600")
    
    Strictly JSON only.
    """
    
    response_text = await call_gemini(prompt)
    try:
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except:
        return {
            "title": "AI Brain Freeze",
            "description": "The AI is resetting. Try again.",
            "duration_days": 1,
            "color": "from-gray-500 to-gray-600"
        }

async def get_workout_suggestion(user: schemas.User, recent_workouts: List[schemas.WorkoutLog]) -> str:
    """
    Generates a workout suggestion prompt and calls an external AI service.
    """
    
    # 1. Construct a detailed prompt
    prompt = f"Act as an elite fitness coach. User Profile:\n"
    prompt += f"- Age: {user.age}, Weight: {user.weight}kg, Goal: {user.goals}\n"

    if recent_workouts:
        prompt += "Recent Activity:\n"
        for workout in recent_workouts[:3]:
            exercise_names = ", ".join([ex.exercise.name for ex in workout.logged_exercises])
            prompt += f"- {workout.name}: {exercise_names}\n"
    else:
        prompt += "No recent activity.\n"

    prompt += "\nSuggest one specific, effective workout session for today. Keep it short and motivating (2 sentences max)."

    # 2. Call Gemini
    response = await call_gemini(prompt)
    if response in ["AI_API_KEY_MISSING", "AI_ERROR"]:
        # Fallback
        import random
        suggestions = [
            "Your consistency is paying off! How about a high-intensity interval training (HIIT) session today?",
            "Consider a focused back and biceps workout to ensure balanced muscle development.",
            "A leg day focusing on squats and lunges would be great for your goals.",
            "How about a dynamic full-body session today? Boost that metabolism!"
        ]
        return random.choice(suggestions)
        
    return response
