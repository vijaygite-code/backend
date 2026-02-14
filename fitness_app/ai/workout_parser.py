import json
import logging
from .. import schemas
from .gemini_api import _call_gemini_api

logger = logging.getLogger(__name__)

async def parse_workout_text(text: str) -> schemas.WorkoutLogCreate:
    """
    Parses natural language workout text into a structured WorkoutLogCreate object.
    """
    
    system_prompt = """
    You are an AI assistant that parses workout logs.
    Convert the user's natural language description of a workout into a strict JSON format.
    
    Input: "I did chest press with 20kg dumbbells for 3 sets of 12 reps"
    Output JSON Schema:
    {
        "name": "Workout Name (infer from exercises, e.g., 'Chest Day')",
        "date": "YYYY-MM-DD" (use today's date if not specified, format as string),
        "notes": "Original text or extra notes",
        "logged_exercises": [
            {
                "exercise_id": null (we will map this later, but try to find name),
                "exercise_name_guess": "Chest Press", 
                "notes": "Dumbbells",
                "sets": [
                    {
                        "set_number": 1,
                        "reps": 12,
                        "weight": 20.0,
                        "weight_unit": "kg"
                    },
                     {
                        "set_number": 2,
                        "reps": 12,
                        "weight": 20.0,
                        "weight_unit": "kg"
                    },
                     {
                        "set_number": 3,
                        "reps": 12,
                        "weight": 20.0,
                        "weight_unit": "kg"
                    }
                ]
            }
        ]
    }
    
    Rules:
    - If sets are implied (e.g. "3 sets of 10"), generate 3 set objects.
    - If weight unit is missing, assume 'kg' or infer.
    - Output ONLY valid JSON. Do not include markdown formatting ```json ... ```.
    """
    
    prompt = f"{system_prompt}\n\nUser Input: {text}\nJSON Output:"
    
    response_text = await _call_gemini_api(prompt)
    
    # cleaning
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(response_text)
        # Note: In a real app, we need to map "exercise_name_guess" to actual DB IDs. 
        # For this MVP, we might return a simpler structure or just this raw JSON for the frontend to confirm/fill IDs.
        return data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from AI: {response_text}")
        raise ValueError("AI failed to parse workout.")

