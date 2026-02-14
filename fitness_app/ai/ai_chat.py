import logging
from typing import List, Dict
from pydantic import BaseModel
from .gemini_api import _call_gemini_api
from .. import models

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

async def chat_with_coach(request: ChatRequest) -> str:
    """
    Handles chat interaction with the AI Coach.
    Constructs a prompt with history and system context.
    """
    
    system_prompt = """
    You are an expert AI Fitness Coach for the 'FitnessPro' app.
    Your goal is to help users with their workouts, nutrition, and motivation.
    
    Guidelines:
    - Be encouraging, professional, and concise.
    - Provide evidence-based advice but disclaim that you are an AI, not a doctor.
    - If asked about the user's data (weight, workouts), you can say you don't have access to live data in this chat yet.
    - Keep answers under 150 words unless asked for a detailed plan.
    """

    # Construct the full prompt context
    full_prompt = f"{system_prompt}\n\nChat History:\n"
    for msg in request.history[-5:]: # Keep last 5 messages for context window
        full_prompt += f"{msg.role.capitalize()}: {msg.content}\n"
    
    full_prompt += f"User: {request.message}\nAssistant:"
    
    # Call Gemini
    response_text = await _call_gemini_api(full_prompt)
    return response_text
