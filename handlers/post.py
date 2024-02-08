import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    GetAppPostSchema
)
from typing import List, Dict
from .database import get_db
from models.model import PostModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination
router = APIRouter()
auth_handler = AuthToken()


@router.get("/posts", tags=["post"])#, response_model=Dict[str,List[GetAppPostSchema]])
async def get_post(
page: int = 1 , per_page: int=10,
    category:str=None,shop:str="shop1",
    db: Session = Depends(get_db)
):   
    if category:
        logger.info(f"Category: {category}")
        count = db.query(PostModel).filter(PostModel.category==category).count()
        meta_data =  pagination(page,per_page,count)
        post_data = db.query(PostModel).filter(PostModel.category==category).order_by(desc(PostModel.publishdate)).limit(per_page).offset((page - 1) * per_page).all()
        return {"post":post_data,"meta":meta_data}
    else:
        logger.info("All Post")
        count = db.query(PostModel).filter(PostModel.shop==shop).count()
        meta_data =  pagination(page,per_page,count)
        post_data = db.query(PostModel).filter(PostModel.shop==shop).order_by(desc(PostModel.publishdate)).limit(per_page).offset((page - 1) * per_page).all()
        return {"post":post_data,"meta":meta_data}


@router.get("/posts/{id}", tags=["post"], response_model=Dict[str,GetAppPostSchema])
def get_post_byid(id: int, db: Session = Depends(get_db)):
    post_data = db.get(PostModel, id)
    if not post_data:
        raise HTTPException(status_code=404, detail="Post ID not found.")
    return {"post":post_data}


@router.get("/similarposts", tags=["post"])#, response_model=Dict[str,List[GetAppPostSchema]])
async def get_post_bycategory(
page: int = 1 , per_page: int=10,
    category:str="",
    db: Session = Depends(get_db)
):
    logger.info(f"Category: {category}")
    post_data = db.query(PostModel).filter(PostModel.category==category).order_by(desc(PostModel.publishdate)).limit(5).all()
    return {"similarpost":post_data}