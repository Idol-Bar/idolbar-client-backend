import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser
)
from typing import List, Dict
from .database import get_db
from models.model import BannerModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination

from fastapi.encoders import jsonable_encoder
router = APIRouter()
auth_handler = AuthToken()


@router.get("/banners", tags=["banner"])
async def get_app_banners(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db)
):
    banners = db.query(BannerModel).order_by(desc(BannerModel.createdate)).all()
    return {"banner":banners}