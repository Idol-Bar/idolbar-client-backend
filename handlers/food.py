import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    FoodSchemaWithMeta,
    FoodCategorySchemaWithMeta
)
from typing import List, Dict
from .database import get_db
from models.model import FoodModel,FoodCategoryModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination
from firebase_admin import messaging
router = APIRouter()
auth_handler = AuthToken()

@router.get("/foodCategories", tags=["food"], response_model=FoodCategorySchemaWithMeta)
async def get_food_categories(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(FoodCategoryModel).count()
    meta_data =  pagination(page,per_page,count)
    categories = db.query(FoodCategoryModel).order_by(desc(FoodCategoryModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"foodCategory":categories,"meta":meta_data}


@router.get("/foods", tags=["food"],response_model=FoodSchemaWithMeta)
async def get_food(
page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(FoodModel).count()
    meta_data =  pagination(page,per_page,count)
    post_data = db.query(FoodModel).order_by(desc(FoodModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"food":post_data,"meta":meta_data}