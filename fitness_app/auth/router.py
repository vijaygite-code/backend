from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import random
import string
import logging

from .. import crud, models, schemas
from . import auth, email_utils
from ..core.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])
# Legacy support for /token and /users at root if needed, or we can move them here.
# User asked to "fix create account" and "forget password".

logger = logging.getLogger(__name__)

# --- Login ---
@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# --- Register ---
@router.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    if user.username:
        db_username = db.query(models.User).filter(models.User.username == user.username).first()
        if db_username:
            raise HTTPException(status_code=400, detail="Username already taken")

    new_user = crud.create_user(db=db, user=user)
    
    # Trigger AI Welcome Email
    background_tasks.add_task(email_utils.send_welcome_email, user.email, user.username or "Athlete")
    
    return new_user

# --- Forgot Password ---

class ForgotPasswordRequest(schemas.BaseModel):
    email: str

class VerifyOTPRequest(schemas.BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(schemas.BaseModel):
    email: str
    otp: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email is registered, an OTP will be sent."}
    
    # Generate OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Save OTP
    # Check if existing reset request exists
    existing_reset = db.query(models.PasswordReset).filter(models.PasswordReset.email == request.email).first()
    if existing_reset:
        existing_reset.otp = otp
        existing_reset.expires_at = datetime.utcnow() + timedelta(minutes=15)
    else:
        new_reset = models.PasswordReset(email=request.email, otp=otp, expires_at=datetime.utcnow() + timedelta(minutes=15))
        db.add(new_reset)
    
    db.commit()
    
    # Send Email
    email_utils.send_email(request.email, "Gym App - Password Reset OTP", f"Your OTP is: {otp}")
    
    return {"message": "If the email is registered, an OTP will be sent."}

@router.post("/verify-otp")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    reset_entry = db.query(models.PasswordReset).filter(models.PasswordReset.email == request.email).first()
    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    # Check expiry (simple check, assume dates are naive utc for now or timezone aware consistent)
    # models.PasswordReset.expires_at is DateTime
    if reset_entry.expires_at < datetime.utcnow():
         raise HTTPException(status_code=400, detail="OTP expired")
         
    if reset_entry.otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    return {"message": "OTP verified"}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Verify OTP again to be safe
    reset_entry = db.query(models.PasswordReset).filter(models.PasswordReset.email == request.email).first()
    if not reset_entry or reset_entry.otp != request.otp or reset_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid OTP or expired")
    
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update password
    # We need a function in crud or auth to hash and update
    hashed_password = auth.get_password_hash(request.new_password)
    user.hashed_password = hashed_password
    db.commit()
    
    # Delete reset entry
    db.delete(reset_entry)
    db.commit()
    
    return {"message": "Password reset successful"}
