import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    PayPointSchema,
    SharePointSchema,
    SharePointWithPhonSchema
)
from typing import List, Dict
from .database import get_db
from models.model import EndUser,Transition,Point,PointLogs,Tier,TierRule,Money
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from modules.utils import pagination
from sqlalchemy import desc,func,and_
router = APIRouter()
auth_handler = AuthToken()


@router.post("/paypoints", tags=["point"])
async def pay_point(
    request: Request, point_info: PayPointSchema, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    #current_user = {"id":1}
    logger.info(point_info.dict())
    owner = db.query(EndUser).get(current_user["id"])
    owner_points_count = db.query(Point).filter(Point.owner_id == current_user["id"]).all()
    logger.info(len(owner_points_count))
    if len(owner_points_count)>int(point_info.unit):
        logger.info("Pay Point")
        db_points = db.query(Point).limit(point_info.unit).all()
        for point in db_points:
            new_transition = Transition(fromUser=owner.username,toUser="admin",status="success")
            point.owner = None
            point.transitions.append(new_transition)
        db.commit()
        return  {"status":f"You send {point_info.unit} points to Admin","wallet":f"{len(owner_points_count)} points","pay":f"{point_info.unit} points","You Left:":f"{len(owner_points_count)-point_info.unit} points"}
    return HTTPException(status_code=400, detail="Not Enought Amount")


@router.post("/sharepoints", tags=["point"])
async def share_point(
    request: Request, point_info: SharePointSchema, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    #current_user = {"id":1}
    if current_user["id"] == point_info.userId:
        raise HTTPException(status_code=400, detail="You Can't Share Yourself.")
    logger.info(point_info.dict())
    owner = db.query(EndUser).get(current_user["id"])
    tier = db.query(Tier).filter_by(user_id=current_user["id"]).first()
    receive = db.query(EndUser).get(point_info.userId)
    owner_points_count = db.query(Point).filter(Point.owner_id == current_user["id"]).all()
    logger.info(len(owner_points_count))
    if len(owner_points_count)>int(point_info.unit):
        logger.info("Take Amount")
        db_points = db.query(Point).filter(Point.owner_id == current_user["id"]).limit(point_info.unit).all()
        for point in db_points:
            logger.info("count")
            new_transition = Transition(fromUser=owner.username,toUser=receive.username,status="success")
            point.owner = receive
            point.owner_id= receive.id
            point.transitions.append(new_transition)
        pay_point_log = PointLogs(amount=0,point=point_info.unit,tier=tier.name,username=owner.username,
                        phoneno=owner.phoneno,status="Share",fromUser=owner.username,toUser=receive.username)
        db.add(pay_point_log)
        db.commit()
        return  {"status":f"You send  {point_info.unit} points to {receive.username}","wallet":f"{len(owner_points_count)} points","pay":f"{point_info.unit} points","You Left:":f"{len(owner_points_count)-point_info.unit} points"}
    return HTTPException(status_code=400, detail="Not Enought Amount")

@router.post("/sharepts/phone", tags=["point"])
async def share_point_byphone(
    request: Request, point_info: SharePointWithPhonSchema, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    #current_user = {"id":1}
    logger.info(point_info.dict())
    owner = db.query(EndUser).get(current_user["id"])
    tier = db.query(Tier).filter_by(user_id=current_user["id"]).first()
    receive = db.query(EndUser).filter(EndUser.phoneno ==point_info.phoneno).first()
    if not receive:
        logger.info("No User with Phone")
        raise HTTPException(status_code=400, detail="User Not Found.")
    if current_user["id"] == receive.id:
        raise HTTPException(status_code=400, detail="You Can't Share Yourself.")
    try:
        sender_money = db.query(func.sum(Money.amount)).filter(Money.user_id == str(current_user["id"])).scalar()
        sender_unit = sender_money if sender_money is not None else 0
        sender_tier = db.query(TierRule).filter(and_(TierRule.lower <= sender_unit, TierRule.higher >= sender_unit)).first()
        tier1 = sender_tier.name if sender_tier else "Unavaliable"
        logger.info(f"Sender Tier : ${tier1}")

        receiver_money = db.query(func.sum(Money.amount)).filter(Money.user_id == str(receive.id)).scalar()
        receiver_unit = receiver_money if receiver_money is not None else 0
        receiver_tier = db.query(TierRule).filter(and_(TierRule.lower <= receiver_unit, TierRule.higher >= receiver_unit)).first()
        tier2 = receiver_tier.name if receiver_tier else "Unavaliable"
        logger.info(f"Receiver Tier : ${tier2}")
        if tier1!=tier2:
            logger.info(f"{tier1} can't send to {tier2}")
            raise HTTPException(status_code=400, detail=f"${tier1} can't send to ${tier2}")
    except  Exception  as e:
        print(e)
        logger.info("Tier Check Failed")
    owner_points_count = db.query(Point).filter(Point.owner_id == current_user["id"]).all()
    logger.info(len(owner_points_count))
    if len(owner_points_count)>int(point_info.unit):
        logger.info("Take Amount")
        db_points = db.query(Point).filter(Point.owner_id == current_user["id"]).limit(point_info.unit).all()
        for point in db_points:
            logger.info("count")
            new_transition = Transition(fromUser=owner.username,toUser=receive.username,status="success")
            point.owner = receive
            point.owner_id= receive.id
            point.transitions.append(new_transition)
        pay_point_log = PointLogs(amount=0,point=point_info.unit,tier=tier.name,username=owner.username,
                        phoneno=owner.phoneno,status="Share",fromUser=owner.username,toUser=receive.username)
        db.add(pay_point_log)
        db.commit()
        return  {"status":f"You send  {point_info.unit} points to {receive.username}","wallet":f"{len(owner_points_count)} points","pay":f"{point_info.unit} points","You Left:":f"{len(owner_points_count)-point_info.unit} points"}
    return HTTPException(status_code=400, detail="Not Enought Amount")

    
    
