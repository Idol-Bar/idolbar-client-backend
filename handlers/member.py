from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from modules.token import AuthToken
from models.schema import UserSchema, LoginSchema,PhoneLoginSchema,RegisterPhoneSchema,CurrentUser,ProfileSchema
from fastapi.logger import logger
from models.model import Tier
from models.model import EndUser as User
from .database import get_db
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging
from firebase_admin import auth as firebase_auth
from modules.dependency import get_current_user
router = APIRouter()

auth_handler = AuthToken()


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
    db_user.status = True
    db.commit()
    db.refresh(db_user)
    return {"user":db_user}

@router.get("/me", tags=["member"], response_model=ProfileSchema)
def get_profile(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    member = db.get(User, current_user["id"])
    if not member:
        raise HTTPException(status_code=404, detail="User ID not found.")
    return member