import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    
)
from typing import List, Dict
from .database import get_db
from models.model import CategoryModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
router = APIRouter()
auth_handler = AuthToken()


@router.get("/categories", tags=["category"])#, response_model=Dict[str,List[GetBookSchema],str,str])
async def get_categories(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db)
):
    count = db.query(CategoryModel).count()
    meta_data =  pagination(page,per_page,count)
    categories = db.query(CategoryModel).order_by(desc(CategoryModel.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return jsonable_encoder({"category":categories,"meta":meta_data})
