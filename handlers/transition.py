import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
   
)
from typing import List, Dict
from .database import get_db
from models.model import  PointLogs,TierRule,Money
from models.model import EndUser as User
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from modules.utils import pagination
from sqlalchemy import desc,or_,func,and_
router = APIRouter()
auth_handler = AuthToken()


@router.get("/transitions", tags=["transition"])
async def get_transition(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    #members = db.query(User).all()
    db_user = db.query(User).get(current_user["id"])
    username = db_user.username
    #username = "ppk"a
    if not db_user:
        raise HTTPException(status_code=404, detail="Users ID not found.")
    count = db.query(PointLogs).filter(or_(PointLogs.fromUser == username, PointLogs.toUser == username)).count()
    meta_data =  pagination(page,per_page,count)
    transition = db.query(PointLogs).filter(or_(PointLogs.fromUser == username, PointLogs.toUser == username)).order_by(desc(PointLogs.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"transition":transition,"meta":meta_data}

@router.get("/transitions/{id}", tags=["transition"])
def get_food_byid(id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    point = db.get(PointLogs, id)
    if not point:
        raise HTTPException(status_code=404, detail="Point ID not found.")
    owner_money = db.query(func.sum(Money.amount)).filter(Money.user_id == str(current_user["id"])).scalar()
    unit = owner_money if owner_money is not None else 0
    tier_rule = db.query(TierRule).filter(and_(TierRule.lower <= unit, TierRule.higher >= unit)).first()
    user_tier = tier_rule.name if tier_rule else "Unavaliable"
    point.tier = user_tier
    return {"transition":point}