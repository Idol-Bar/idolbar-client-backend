from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict
from modules.token import AuthToken
from models.schema import UserSchema, LoginSchema,PhoneLoginSchema,RegisterPhoneSchema,CurrentUser,ProfileSchema,ReserveSchema
from fastapi.logger import logger
from models.model import Tier,Reservation,Tables
from models.model import EndUser as User
from models.model import Point
from .database import get_db
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging
from firebase_admin import auth as firebase_auth
from modules.dependency import get_current_user
from sqlalchemy import func,desc

router = APIRouter()

auth_handler = AuthToken()


@router.put("/update-info", tags=["auth"])
async def update_info(data: RegisterPhoneSchema,db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    db_user = db.query(User).get(current_user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="News ID not found.")
    db_user.username =  data.username
    db_user.birthday =  data.birthday
    db_user.state =  data.state
    db_user.division =  data.division
    db_user.shop = data.shop
    db_user.status = "CONFIRM"
    db.commit()
    db.refresh(db_user)
    return {"user":db_user}

@router.put("/phone-register", tags=["member"])
async def phone_register(data: RegisterPhoneSchema,db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    db_user = db.query(User).get(current_user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="News ID not found.")
    db_user.username =  data.username
    db_user.birthday =  data.birthday
    db_user.state =  data.state
    db_user.division =  data.division
    db_user.shop = data.shop
    db_user.status = "CONFIRM"
    db.commit()
    db.refresh(db_user)
    return {"user":db_user}

# @router.get("/me", tags=["member"], response_model=ProfileSchema)
# def get_profile(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
#     member = db.get(User, current_user["id"])
#     owner_points_count = db.query(Point).filter(Point.owner_id == current_user["id"]).all()
#     if not member:
#         raise HTTPException(status_code=404, detail="User ID not found.")
#     return member

@router.get("/profile/me", tags=["profile"], response_model=Dict[str,ProfileSchema])
async def get_profile(
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    
    user = db.query(User).get(current_user["id"])
    owner_points_count = db.query(Point).filter(Point.owner_id == current_user["id"]).all()
    unit = len(owner_points_count) if owner_points_count is not None else 0
    if not user:
        raise HTTPException(status_code=401, detail="User ID not found.")
    profile_data = {
        "id": user.id,
        "username": user.username,
        "birthday": user.birthday,
        "postImage": user.postImage,
        "phoneno": user.phoneno,
        "createdate": user.createdate,
        "code": user.code,
        "unit":unit,
        "tier": [{"name": tier.name for tier in user.tier}]
    }
    return {"profile":profile_data}

@router.get("/wallet", tags=["member"])
def get_profile(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    member = db.get(User, current_user["id"])
    owner_points_count = db.query(Point).filter(Point.owner_id == current_user["id"]).all()
    if not member:
        raise HTTPException(status_code=404, detail="User ID not found.")
    unit = len(owner_points_count) if owner_points_count is not None else 0
    return {"unit":unit}

@router.get("/profile/reservations", tags=["profile"], response_model=Dict[str,List[ReserveSchema]])
async def get_profile_reservation(
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    reservation = db.query(Reservation).join(Tables, Reservation.tables).filter(Reservation.username==current_user["username"]).order_by(desc(Reservation.createdate)).all()
    return {"reservation":reservation}