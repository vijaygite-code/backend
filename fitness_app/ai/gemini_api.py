# D:/projects/EAM/assistant/fitness_app/gemini_api.py
# This file contains the low-level function for calling the Google Gemini API.

import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Use the provided Gemini API key with a fallback to an environment variable
AI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("API_KEY", "AIzaSyCwR2FJ9FXK2-jMoyHTSYBBi9viIgr8rc0"))
AI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

async def _call_gemini_api(prompt: str, image_data: str = None, mime_type: str = "image/jpeg") -> str:
    """
    A centralized function to call the Gemini API with correct headers.
    Supports multimodal input (text + image).
    image_data: Base64 encoded image string.
    """
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': AI_API_KEY
    }
    
    parts = [{"text": prompt}]
    
    if image_data:
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": image_data
            }
        })
    
    json_data = {
        "contents": [
            {"parts": parts}
        ]
    }

    logger.info(f"Sending prompt to Gemini: {prompt[:200]}... (Image included: {bool(image_data)})")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(AI_API_URL, headers=headers, json=json_data, timeout=60.0) # Increased timeout for images
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
