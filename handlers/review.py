import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    GetReviewSchema,
    CreateAppReviewSchemaRequest
)
from typing import List, Dict
from .database import get_db
from models.model import ReviewModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
router = APIRouter()
auth_handler = AuthToken()


@router.get("/reviews", tags=["review"])#, response_model=Dict[str,List[GetBookSchema],str,str])
async def get_app_review(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db)
):
    count = db.query(ReviewModel).count()
    meta_data =  pagination(page,per_page,count)
    reviews = db.query(ReviewModel).filter(ReviewModel.status=="CONFIRM").order_by(desc(ReviewModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return jsonable_encoder({"review":reviews,"meta":meta_data})


@router.post("/reviews", tags=["review"], response_model=Dict[str,GetReviewSchema])
async def add_app_review(
    request: Request, data: CreateAppReviewSchemaRequest, db: Session = Depends(get_db)
):
    logger.info(data.dict())
    review = ReviewModel(**data.review.dict())
    db.add(review)
    db.commit()
    db.refresh(review)

    return {"review":review}