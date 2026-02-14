from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from .. import models, schemas
from ..auth import auth
from . import models as mind_models
from ..ai import moderator
from datetime import date, timedelta
import json

router = APIRouter(
    prefix="/mind",
    tags=["Gym Mind"]
)

# --- Admin Endpoints ---

@router.get("/tasks")
def get_pending_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db.query(mind_models.MindTask).filter(mind_models.MindTask.status == mind_models.TaskStatus.PENDING).all()

@router.post("/tasks/{task_id}/resolve")
def resolve_task(
    task_id: int,
    action: str, # "approve" or "reject"
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    task = db.query(mind_models.MindTask).filter(mind_models.MindTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if action == "approve":
        task.status = mind_models.TaskStatus.APPROVED
        # Execute action based on type
        if task.type == mind_models.TaskType.CHALLENGE_PROPOSAL:
            # Create the challenge
            content = task.content
            # Ensure dates are parsed if string
            new_challenge = models.Challenge(
                title=content.get("title"),
                description=content.get("description"),
                start_date=date.fromisoformat(content.get("start_date")),
                end_date=date.fromisoformat(content.get("end_date")),
                color=content.get("color", "from-orange-500 to-red-500")
            )
            db.add(new_challenge)
            
    elif action == "reject":
        task.status = mind_models.TaskStatus.REJECTED
        
    db.commit()
    db.commit()
    return {"status": "resolved"}

@router.get("/logs")
def get_monitoring_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db.query(mind_models.MonitoringLog).order_by(mind_models.MonitoringLog.timestamp.desc()).limit(50).all()

# --- User Endpoints ---

from ..ai.gemini_api import _call_gemini_api

# ... (imports remain)

# --- User Endpoints ---

@router.get("/motivation")
async def get_daily_motivation(db: Session = Depends(get_db)):
    today = date.today()
    quote = db.query(mind_models.MotivationQuote).filter(mind_models.MotivationQuote.for_date == today).first()
    if not quote:
        # Generate one via AI
        prompt = "Generate a short, powerful, and unique fitness motivation quote for today. Do not use cliches. Keep it under 20 words. Return ONLY the quote text."
        try:
            quote_text = await _call_gemini_api(prompt)
            # Cleanup quotes if any
            quote_text = quote_text.replace('"', '').strip()
        except Exception as e:
            quote_text = "Consistency is the key to progress." # Fallback

        quote = mind_models.MotivationQuote(text=quote_text, for_date=today)
        db.add(quote)
        db.commit()
        db.refresh(quote)
    return quote

@router.post("/ask")
async def ask_mind(
    query: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Determine Context and Tools based on Role
    system_context = ""
    is_admin = current_user.role == models.UserRole.ADMIN
    
    if is_admin:
        from ..ai import admin_tools
        stats = admin_tools.get_system_stats(db)
        system_context = f"""
        You are 'The Cortex', an advanced AI assistant to the Owner/Admin of FitnessPro.
        You have access to real-time system statistics: {json.dumps(stats)}
        
        Your Goal: Assist the admin in managing the platform. 
        - If asked about user counts, revenue (infer from paid users), or engagement, use the provided stats.
        - Be professional, concise, and insightful.
        - You are talking to the Boss.
        """
    else:
        system_context = """
        You are 'The Gym Mind', a super-intelligent AI governing the FitnessPro ecosystem.
        Your personality is analytical, slightly robotic but encouraging, and highly data-driven.
        Answer the user's question concisely.
        """
    
    full_prompt = f"{system_context}\nUser: {query}\nResponse:"
    
    try:
        answer = await _call_gemini_api(full_prompt)
    except Exception:
        answer = "My processing units are currently overloaded. Please try again later."
    
    escalate = False
    if not is_admin and ("refund" in query.lower() or "cancel" in query.lower() or "human" in query.lower()):
        answer += "\n\n(I have flagged this conversation for human review.)"
        escalate = True
    
    user_query = mind_models.UserQuery(
        user_id=current_user.id,
        question=query,
        answer=answer,
        escalated_to_admin=escalate
    )
    db.add(user_query)
    db.commit()
    
    return {"answer": answer}

# --- System/Test Endpoints ---
@router.post("/generate-challenge")
async def generate_challenge_proposal(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    prompt = """
    Generate a unique fitness challenge idea. 
    Return a JSON object with the following fields:
    - title: string (Creative name)
    - description: string (Short description of rules)
    - color: string (Tailwind gradient class, e.g., 'from-red-500 to-orange-500')
    - duration_days: int (e.g. 7, 30)
    
    Do NOT include markdown formatting or backticks. Just the raw JSON string.
    """
    
    try:
        response_text = await _call_gemini_api(prompt)
        # Clean up potential markdown
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(response_text)
        
        # Calculate dates
        duration = data.get("duration_days", 30)
        start_date = date.today()
        end_date = start_date + timedelta(days=duration)
        
        proposal = {
            "title": data.get("title", "New Challenge"),
            "description": data.get("description", "A new fitness challenge."),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "color": data.get("color", "from-blue-500 to-purple-500")
        }
        
        task = mind_models.MindTask(
            type=mind_models.TaskType.CHALLENGE_PROPOSAL,
            content=proposal,
            status=mind_models.TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        return {"message": "Challenge proposal generated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")
