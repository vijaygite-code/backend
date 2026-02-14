
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..core.database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={404: {"description": "Not found"}},
)

@router.post("/progress", response_model=List[schemas.AnalyticsDataPoint])
def get_analytics(
    request: schemas.AnalyticsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get aggregated analytics data based on the request parameters.
    """
    return crud.get_analytics_data(db=db, user_id=current_user.id, request=request)

# --- Dashboard Widgets ---

@router.post("/widgets", response_model=schemas.DashboardWidget)
def create_widget(
    widget: schemas.DashboardWidgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_widget(db=db, widget=widget, user_id=current_user.id)

@router.get("/widgets", response_model=List[schemas.DashboardWidget])
def read_widgets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_widgets_by_user(db=db, user_id=current_user.id)

@router.put("/widgets/{widget_id}", response_model=schemas.DashboardWidget)
def update_widget(
    widget_id: int,
    widget_update: schemas.DashboardWidgetUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_widget = crud.update_widget(db=db, widget_id=widget_id, widget_update=widget_update, user_id=current_user.id)
    if db_widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    return db_widget

@router.delete("/widgets/{widget_id}")
def delete_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    success = crud.delete_widget(db=db, widget_id=widget_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Widget not found")
    return {"message": "Widget deleted"}

# --- AI Insights ---

@router.post("/ai-insight")
async def get_ai_insight(
    request: schemas.AIInsightRequest,
    current_user: models.User = Depends(auth.get_current_paid_user)
):
    """
    Get AI-generated insight based on the provided context summary.
    """
    try:
        from ..ai import ai_analytics
        insight = await ai_analytics.generate_progress_insight(request.context)
        return {"insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
