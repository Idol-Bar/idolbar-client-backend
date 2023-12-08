import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser
)
from typing import List, Dict
from .database import get_db
from models.model import BannerModel,NotiModel,FaqModel
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
    db: Session = Depends(get_db)#, current_user: CurrentUser = Depends(get_current_user)
):
    banners = db.query(BannerModel).order_by(desc(BannerModel.createdate)).all()
    return {"banner":banners}

@router.get("/notifications", tags=["notification"])
async def get_app_notification(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(current_user["role"])
    count = db.query(NotiModel).count()
    meta_data =  pagination(page,per_page,count)
    notifications = db.query(NotiModel).order_by(desc(NotiModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return jsonable_encoder({"notification":notifications,"meta":meta_data})

@router.get("/faqs", tags=["faq"])#, response_model=Dict[str,List[GetBookSchema],str,str])
async def get_app_faq(
    page: int = 1 , per_page: int=5,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(FaqModel).count()
    meta_data =  pagination(page,per_page,count)
    faq = db.query(FaqModel).order_by(desc(FaqModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return jsonable_encoder({"faq":faq,"meta":meta_data})