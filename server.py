from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.logger import logger
import logging
from fastapi.middleware.cors import CORSMiddleware
import os.path as op
from modules.token import AuthToken
import datetime
from firebase_admin import credentials
import firebase_admin
def create_app():
    app = FastAPI(title="Idolbar",description="NobleTech",)
    cred = credentials.Certificate("idolbar-66fe5-firebase-adminsdk-xtsop-49667f9365.json")
    firebase_app = firebase_admin.initialize_app(cred)
    auth_handler = AuthToken()
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from modules.dependency import AuthHandler
    from handlers import login, auth, upload,member,point,transition,reservation,banner,category,post,food,cart,order
    from handlers.database import SessionLocal, engine
    from modules.dependency import  AuthHandler
    #import models.model as app_model
    import handlers.database as app_model
    from models.model import EndUser as User

    app_model.Base.metadata.create_all(bind=engine)
    logging.basicConfig(
       format='AloDawPyi:{levelname:7} {message}', style='{', level=logging.DEBUG)

    app.include_router(upload.upload_router)
    app.include_router(upload.read_router)
    app.include_router(login.router)
    app.include_router(auth.router)
    app.include_router(member.router,dependencies=[Depends(AuthHandler)])
    app.include_router(point.router)#,dependencies=[Depends(AuthHandler)])
    app.include_router(transition.router,dependencies=[Depends(AuthHandler)])
    #app.include_router(posts.router,dependencies=[Depends(AdminHandler)])
    app.include_router(reservation.router,dependencies=[Depends(AuthHandler)])
    app.include_router(banner.router,dependencies=[Depends(AuthHandler)])
    app.include_router(category.router,dependencies=[Depends(AuthHandler)])
    app.include_router(post.router,dependencies=[Depends(AuthHandler)])
    app.include_router(food.router,dependencies=[Depends(AuthHandler)])
    app.include_router(cart.router,dependencies=[Depends(AuthHandler)])
    app.include_router(order.router,dependencies=[Depends(AuthHandler)])
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Database Startup Complete")

    return app


app = create_app()
