import httpx
import os
import logging
from typing import List
from . import schemas, models # Import models for type hint

logger = logging.getLogger(__name__)

# Use the provided Gemini API key with a fallback to an environment variable
AI_API_KEY = os.getenv("API_KEY", "AIzaSyCwR2FJ9FXK2-jMoyHTSYBBi9viIgr8rc0")
AI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

async def _call_gemini_api(prompt: str) -> str:
    """A centralized function to call the Gemini API with correct headers."""
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': AI_API_KEY
    }
    
    json_data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    logger.info(f"Sending prompt to Gemini: {prompt[:200]}...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(AI_API_URL, headers=headers, json=json_data, timeout=30.0)
            response.raise_for_status()
            logger.info(f"Received response from Gemini: {response.text[:200]}...")
            # Extract text from the response
            candidates = response.json().get('candidates', [])
            if candidates and 'content' in candidates[0] and 'parts' in candidates[0]['content']:
                return candidates[0]['content']['parts'][0].get('text', '').strip()
            else:
                logger.error("Unexpected Gemini API response format.")
                return "I'm sorry, I received an unexpected response. Please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API request failed with status {e.response.status_code}: {e.response.text}")
            return "I'm sorry, there was an error with the AI service. The developers have been notified."
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling Gemini API: {e}")
            return "I'm having a little trouble connecting right now. Please try again in a moment."

async def get_chat_response(user: models.User, history: List[schemas.ChatMessage], new_message: str) -> str:
    """Generates a chat response from the AI coach using the Gemini API."""
    
    conversation_history = ""
    for message in history:
        role = "User" if message.role == 'user' else "Coach"
        conversation_history += f"{role}: {message.content}\n"
    
    conversation_history += f"User: {new_message}"

    # Prepare habit data for the prompt, handling potential empty lists
    # Prepare habit data for the prompt
    habit_summary = "No habit data logged yet."
    if user.habit_entries:
        # Format the last few habit entries for the prompt
        recent_habits = sorted(user.habit_entries, key=lambda h: h.date, reverse=True)[:3]
        habit_summary = "\n".join([
            f"- On {h.date}: Sleep: {h.sleep_hours or 'N/A'}h, Water: {h.water_liters or 'N/A'}L, Steps: {h.steps or 'N/A'}" 
            for h in recent_habits
        ])

    # Prepare meal data
    meal_summary = "No recent meals logged."
    if user.meal_logs:
        recent_meals = sorted(user.meal_logs, key=lambda m: m.date, reverse=True)[:5]
        meal_summary = "\n".join([
            f"- On {m.date} ({m.meal_type}): {m.description} (~{m.calories} cal, P:{m.protein_g}g, C:{m.carbs_g}g, F:{m.fats_g}g)"
            for m in recent_meals
        ])

    # Prepare workout data
    workout_summary = "No recent workouts logged."
    if user.workout_logs:
        recent_workouts = sorted(user.workout_logs, key=lambda w: w.date, reverse=True)[:5]
        workout_summary = "\n".join([
            f"- On {w.date}: {w.name} (Notes: {w.notes or 'None'})"
            for w in recent_workouts
        ])

    # User Stats
    user_stats = f"""
    - Age: {user.age if user.age else 'N/A'}
    - Weight: {user.weight}kg
    - Height: {user.height}cm
    - Goals: {user.goals if user.goals else 'Not specified'}
    """

    system_prompt = f"""You are Coach Alex, an elite, encouraging, and highly technical AI fitness coach.
Your goal is to help the user achieve their fitness goals ({user.goals if user.goals else 'general fitness'}) by analyzing their data and providing specific, actionable advice.

User Profile:
{user_stats}

User's Recent Activity:
[Workouts]
{workout_summary}

[Habits]
{habit_summary}

[Meals]
{meal_summary}

Conversation History:
{conversation_history}

Coach Alex:"""

    try:
        return await _call_gemini_api(system_prompt)
    except Exception as e:
        logger.error(f"Error generating chat response, possibly due to DB issue: {e}")
        return "I'm having trouble accessing your full profile right now. Please ensure your database is up to date. If the problem persists, contact support."
