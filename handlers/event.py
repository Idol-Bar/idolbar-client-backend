import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    EventSchema
)
from typing import List, Dict
from .database import get_db
from models.model import EventModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination
from datetime import date
router = APIRouter()
auth_handler = AuthToken()


@router.get("/events", tags=["events"])#, response_model=Dict[str,List[GetBannerSchema]])
async def get_events(
    page: int = 1 , per_page: int=8,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(EventModel).count()
    meta_data =  pagination(page,per_page,count)
    events = db.query(EventModel).order_by(desc(EventModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"event":events,"meta":meta_data}

@router.get("/coming-events", tags=["events"])
async def get_coming_events(
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    events = db.query(EventModel).filter(EventModel.reservedate > date.today()).order_by(desc(EventModel.createdate)).all()
    return {"event":events}