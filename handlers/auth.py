from fastapi import APIRouter, Request
from modules.token import AuthToken
from fastapi.logger import logger
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Request, Security, HTTPException

router = APIRouter()
auth_handler = AuthToken()
security = HTTPBearer()
"""
@router.post("/refresh_token")
def refresh_token(request: Request):
    refresh_token = request.current_user.credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {"access_token": new_token}"""

@router.post('/refresh_token', tags=["auth"])
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token,new_refresh_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token,"refresh_token": new_refresh_token}

#
# @router.post("/secret")
# def secret_data(request: Request):
#     logger.info("Secret Route")
#     logger.info(request.current_user.credentials.credentials)
#     # token = credentials.credentials
#     # if(auth_handler.decode_token(token)):
#     return "Top Secret data only authorized users can access this info"
