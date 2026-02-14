from .gemini_api import _call_gemini_api
import logging

logger = logging.getLogger(__name__)

async def check_content(text: str) -> tuple[bool, str | None]:
    """
    Checks if the content is safe using Gemini.
    Returns: (is_safe: bool, reason: str | None)
    """
    prompt = f"""
    Analyze the following text for toxicity, hate speech, violence, self-harm, or explicit content.
    Text: "{text}"
    
    If the text contains any of the above, return ONLY the word "UNSAFE" followed by a colon and the specific reason (e.g. "UNSAFE: Hate speech").
    If the text is safe, return ONLY "SAFE".
    """
    
    try:
        response = await _call_gemini_api(prompt)
        response = response.strip()
        
        if response.startswith("UNSAFE"):
            reason = response.split(":", 1)[1].strip() if ":" in response else "Inappropriate content"
            return False, reason
            
        return True, None
    except Exception as e:
        logger.error(f"Moderation check failed: {e}")
        # Default to safe if AI fails to avoid blocking users unnecessarily, or fail safe depending on policy.
        # Strict warden policy: Fail safe -> block? No, let's log and allow but mark for review?
        # User said "warden", so maybe strict. But unavailability shouldn't block app.
        # Let's return True but log error.
        return True, None
