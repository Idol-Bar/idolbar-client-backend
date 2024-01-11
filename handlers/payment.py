import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    PaymentSchema,
)
from typing import List, Dict
from .database import get_db
from models.model import PaymentModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from modules.utils import pagination
router = APIRouter()
auth_handler = AuthToken()


@router.get("/payments", tags=["payment"])#, response_model=Dict[str,List[GetBannerSchema]])
async def get_payment(
    shop: str = "shop1",
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    payment = db.query(PaymentModel).filter(PaymentModel.shop==shop).order_by(desc(PaymentModel.createdate)).all()
    return {"payment":payment}
