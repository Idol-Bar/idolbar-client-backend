import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    FoodSchemaWithMeta,GetFoodSchema,
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


# @router.get("/foods", tags=["food"],response_model=FoodSchemaWithMeta)
# async def get_food(
# page: int = 1 , per_page: int=10,
#     db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
# ):
#     count = db.query(FoodModel).count()
#     meta_data =  pagination(page,per_page,count)
#     post_data = db.query(FoodModel).order_by(desc(FoodModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
#     return {"food":post_data,"meta":meta_data}


@router.get("/foods/{id}", tags=["food"], response_model=Dict[str,GetFoodSchema])
def get_food_byid(id: int, db: Session = Depends(get_db)):
    food = db.get(FoodModel, id)
    if not food:
        raise HTTPException(status_code=404, detail="Food ID not found.")
    return {"food":food}

@router.get("/foods", tags=["food"], response_model=Dict[str,List[GetFoodSchema]])
async def get_food(
    shop:str="shop1",category:str="all",
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    if category=="all":
        food = db.query(FoodModel).filter(FoodModel.shop==shop).order_by(desc(FoodModel.createdate)).all()
        return {"food":food}
    else:
        food = db.query(FoodModel).filter(FoodModel.shop==shop,FoodModel.category_id==category).order_by(desc(FoodModel.createdate)).all()
        return {"food":food}

@router.get("/foods/filter/{category}", tags=["food"],response_model=FoodSchemaWithMeta)
async def get_food_bycategory(
    category: str,page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(FoodModel).join(FoodCategoryModel).filter(FoodCategoryModel.name == category).count()
    meta_data =  pagination(page,per_page,count)
    food_data = db.query(FoodModel).join(FoodCategoryModel).filter(FoodCategoryModel.name == category).order_by(desc(FoodModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"food":food_data,"meta":meta_data}