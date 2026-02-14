import os
import logging
import httpx
from typing import List, Optional
from pydantic import BaseModel
from .. import schemas, models

logger = logging.getLogger(__name__)

AI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

class WorkoutPlanRequest(BaseModel):
    days_per_week: int
    duration_minutes: int
    fitness_level: str # Beginner, Intermediate, Advanced
    equipment: Optional[str] = "Gym equipment"
    focus_area: Optional[str] = "Full Body"

async def _call_gemini_api(prompt: str) -> str:
    """Helper to call Gemini API."""
    if not AI_API_KEY:
        logger.error("GEMINI_API_KEY is not set.")
        return "AI service is currently unavailable."

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': AI_API_KEY
    }
    
    json_data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(AI_API_URL, headers=headers, json=json_data, timeout=45.0)
            response.raise_for_status()
            
            candidates = response.json().get('candidates', [])
            if candidates and 'content' in candidates[0] and 'parts' in candidates[0]['content']:
                return candidates[0]['content']['parts'][0].get('text', '').strip()
            else:
                return "Failed to generate content."
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return "An error occurred while generating the workout plan."

async def generate_workout_plan(user: models.User, request: WorkoutPlanRequest) -> str:
    """Generates a personalized workout plan."""
    
    prompt = f"""
    Act as an elite personal trainer. Create a personalized {request.days_per_week}-day weekly workout plan for a client with the following profile:

    **Client Profile:**
    - Age: {user.age}
    - Weight: {user.weight} kg
    - Height: {user.height} cm
    - Goal: {user.goals}
    
    **Preferences:**
    - Days per week: {request.days_per_week}
    - Duration per session: {request.duration_minutes} minutes
    - Fitness Level: {request.fitness_level}
    - Equipment Access: {request.equipment}
    - Focus Area: {request.focus_area}

    **Instructions:**
    - Provide a structured plan for each day (Day 1, Day 2, etc.).
    - Include exercises, sets, reps, and brief rest instructions.
    - Provide a warm-up and cool-down routine.
    - Give a brief nutritional tip based on their goal.
    - Format usage of Markdown is encouraged for readability.
    """
    
    return await _call_gemini_api(prompt)
