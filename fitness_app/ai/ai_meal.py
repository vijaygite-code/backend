import json
import logging
from .gemini_api import _call_gemini_api

logger = logging.getLogger(__name__)

async def analyze_meal_image(image_base64: str) -> dict:
    """
    Analyzes a meal image using Gemini Vision to extract nutritional information.
    Returns a dictionary with estimated calories and macros.
    """
    
    prompt = """
    Analyze this image of a meal. Identify the food items and estimate the total calories, protein, carbs, and fats.
    Return the result ONLY as a JSON object with the following keys:
    {
        "description": "Short description of the meal (e.g., 'Grilled Chicken with Broccoli')",
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fats_g": 0
    }
    Do not include markdown formatting like ```json ... ```. Just the raw JSON string.
    If you cannot identify food, return null for values but provide a description explaining why.
    """

    try:
        response_text = await _call_gemini_api(prompt, image_data=image_base64)
        
        # Clean up potential markdown formatting
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        meal_data = json.loads(response_text)
        return meal_data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse AI response as JSON: {response_text}")
        return {
            "description": "Error parsing AI response. Please try again.",
            "calories": None,
            "protein_g": None,
            "carbs_g": None,
            "fats_g": None
        }
    except Exception as e:
        logger.error(f"Error analyzing meal: {e}")
        return {
            "description": "Error analyzing image.",
            "calories": None,
            "protein_g": None,
            "carbs_g": None,
            "fats_g": None
        }
