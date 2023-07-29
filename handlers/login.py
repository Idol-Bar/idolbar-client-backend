from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from modules.token import AuthToken
from models.schema import UserSchema, LoginSchema
from fastapi.logger import logger
from models.model import User
from .database import get_db
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging
router = APIRouter()

auth_handler = AuthToken()


@router.post("/login", tags=["auth"])
def login(user_details: LoginSchema, db: Session = Depends(get_db)):
    logger.info(user_details)
    user = db.query(User).filter(User.username == user_details.username).first()
    if user is None:
        return HTTPException(status_code=400, detail="Invalid username")
    if not user.active:
        return HTTPException(status_code=400, detail="Invalid user")
    if not auth_handler.verify_password(user_details.password, user.password):
        return HTTPException(status_code=400, detail="Invalid password")
    if not user.role[0].name=="admin":
        return HTTPException(status_code=400, detail="Invalid user")
    access_token = auth_handler.encode_token(user.username, user.role[0].name, user.id)
    refresh_token = auth_handler.encode_refresh_token(
        user.username, user.role[0].name, user.id
    )
    content = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "username": user.username,
        "role": user.role[0].name,
    }
    logger.info(content)
    response = JSONResponse(content=jsonable_encoder(content))
    # response.set_cookie(key="jwt", value=access_token, httponly=True)
    # response.set_cookie(key="access_token",
    #                     value=f"Bearer {access_token}", httponly=True)
    #response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response
