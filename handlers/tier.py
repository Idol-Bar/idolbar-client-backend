import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,

)
from typing import List, Dict
from .database import get_db
from models.model import TierRule
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from modules.utils import pagination
from sqlalchemy import desc
router = APIRouter()
auth_handler = AuthToken()


@router.get("/tiers", tags=["tier"])
async def get_tiers(
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    tier = db.query(TierRule.id,TierRule.name,TierRule.createdate,TierRule.postImage,TierRule.description).order_by(desc(TierRule.createdate)).all()
    return {"tier":tier}

@router.get("/tier/{name}", tags=["tier"])
def get_tiers_byname(name: str, db: Session = Depends(get_db)):
    tier_data = db.query(TierRule).filter(TierRule.name == name).first()
    return {"tier":tier_data}