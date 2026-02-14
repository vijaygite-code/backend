from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..core.database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """
    Get all users. ADMIN ONLY.
    """
    return crud.get_all_users(db, skip=skip, limit=limit)

@router.put("/{user_id}/role")
def update_role(
    user_id: int, 
    role: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """
    Update user role (admin, trainer, paid, user). ADMIN ONLY.
    """
    # Validation
    if role not in [models.UserRole.ADMIN, models.UserRole.TRAINER, models.UserRole.PAID, models.UserRole.unpaid]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user = crud.update_user_role(db, user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """
    Delete a user. ADMIN ONLY.
    """
    if user_id == current_user.id:
         raise HTTPException(status_code=400, detail="Cannot delete yourself")
         
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
