
import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    
logger = logging.getLogger(__name__)

async def generate_progress_insight(context_summary: str) -> str:
    """
    Generates a short, personalized insight or motivational message based on the user's data context.
    """
    if not GENAI_API_KEY:
        return "AI Pilot is offline. Great work keeping active!"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        You are an elite fitness coach.
        Analyze this user's recent workout data summary: "{context_summary}"
        
        If the trend is positive (progress up), give a short, high-energy compliment (max 2 sentences).
        If the trend is negative/flat, give a short, empathetic motivational quote about recovery and consistency (max 2 sentences).
        
        Do not use technical jargon. Be human, encouraging, and brief.
        """
        
        response = await model.generate_content_async(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error generating AI insight: {e}")
        return "Consistency is key! Keep showing up."
