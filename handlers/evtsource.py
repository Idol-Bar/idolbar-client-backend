from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from modules.token import AuthToken
from models.schema import UserSchema, LoginSchema
from fastapi.logger import logger
from models.model import EndUser as User
from .database import get_db
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging
import psycopg2
import asyncio
from configs.setting import Settings

settings = Settings()

router = APIRouter()
STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond

@router.get('/noti', tags=["evtsource"])
async def message_stream(request: Request):
    async def event_generator():
        conn = psycopg2.connect(host=settings._dbhost, dbname=settings._dbname, user=settings._dbuser, password=settings._dbpass)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f"LISTEN match_updates;")
        while True:
            conn.poll()
            if await request.is_disconnected():
                break
            for notify in conn.notifies:
                notify = conn.notifies.pop()
                if notify.payload == 'TERMINATE':
                    return
                yield {"event":"notification","id":"1","data":notify.payload,"retry": RETRY_TIMEOUT,}
            await asyncio.sleep(STREAM_DELAY)
    response = EventSourceResponse(event_generator())
    return EventSourceResponse(event_generator())