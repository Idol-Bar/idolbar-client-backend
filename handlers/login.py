from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from modules.token import AuthToken
from models.schema import UserSchema, LoginSchema,PhoneLoginSchema,RegisterPhoneSchema
from fastapi.logger import logger
from models.model import Tier
from models.model import EndUser as User
from .database import get_db
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging
from firebase_admin import auth as firebase_auth
router = APIRouter()

auth_handler = AuthToken()

@router.post("/phone-login", tags=["auth"])
def login(user_details: PhoneLoginSchema, db: Session = Depends(get_db)):
    logger.info(user_details)
    user_info_fb = firebase_auth.verify_id_token(user_details.verificationID)
    logger.info(user_info_fb["phone_number"])
    user = db.query(User).filter(User.phoneno == user_info_fb["phone_number"]).first()
    if user is None:
        tier = Tier(name="gold")
        db_user = User(
                    phoneno=user_info_fb["phone_number"],
                    tier=[tier],
                    status=False
                )
        db.add(db_user)
        db.add(tier)
        db.commit()
        access_token = auth_handler.encode_token( "user","gold", db_user.id)
        refresh_token = auth_handler.encode_refresh_token(
            db_user.username, db_user.tier[0].name, db_user.id
        )
        content = {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "id":db_user.id,
            #"username": user.username,
            "role": db_user.tier[0].name,
            "isnew" : True
        }
        logger.info(content)
        response = JSONResponse(content=jsonable_encoder(content))
        return response
    else:
        if not user.active:
            return HTTPException(status_code=400, detail="Invalid user")
        access_token = auth_handler.encode_token(user.username, user.tier[0].name, user.id)
        refresh_token = auth_handler.encode_refresh_token(
            user.username, user.tier[0].name, user.id
        )
        content = {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "id":user.id,
            "username": user.username,
            "role": user.tier[0].name,
            "isnew" : False
        }
        logger.info(content)
        response = JSONResponse(content=jsonable_encoder(content))
        return response


