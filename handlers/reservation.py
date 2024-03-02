import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    ReserveSchema,
    CreateReserveSchemaRequest,
    TablesSchema,
    CreateTableSchemaRequest,ReserveSchemaWithMeta,RestableScema,CreateOrderSchemaRequest,GetReservedOrder
)
from typing import List, Dict
from .database import get_db
from models.model import Reservation, Tables,Cart,Order,OrderItem,AdminNotiModel
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from modules.utils import pagination
from sqlalchemy import desc,func,text
from datetime import datetime, date
from uuid import uuid4
from pydantic import parse_obj_as
import json
import psycopg2
from configs.setting import Settings

settings = Settings()

conn = psycopg2.connect(host=settings._dbhost, dbname=settings._dbname, user=settings._dbuser, password=settings._dbpass)
cursor = conn.cursor()
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

router = APIRouter()
auth_handler = AuthToken()


@router.get("/reservations", tags=["reservation"], response_model=Dict[str,List[ReserveSchema]])
async def get_reservation(
    tables:str = None,reservedate:date = date.today(),shop:str = None,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    if tables:
        reservation = db.query(Reservation).join(Tables, Reservation.tables).filter(func.date(Reservation.reservedate)==reservedate,Tables.name==tables,Tables.shop==shop).order_by(desc(Reservation.createdate)).all()
        return {"reservation":reservation}
    else:
        return {"reservation":[]}


@router.get("/reserveLists", tags=["reservation"],response_model=ReserveSchemaWithMeta)
async def get_reservelist(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    print(current_user)
    count = db.query(Reservation).filter(Reservation.userId==current_user["id"]).count()
    meta_data =  pagination(page,per_page,count)
    reservation = db.query(Reservation).join(Tables, Reservation.tables).filter(Reservation.userId==current_user["id"],Reservation.active==True).order_by(desc(Reservation.createdate)).all()
    return {"reserveList":reservation,"meta":meta_data}

@router.get("/reserveLists/{id}", tags=["reservation"], response_model=Dict[str,ReserveSchema])
def get_reserve_byid(id: int, db: Session = Depends(get_db)):
    reservedata = db.get(Reservation, id)
    if not reservedata:
        raise HTTPException(status_code=404, detail="Reservation ID not found.")
    return {"reserveList":reservedata}

@router.delete("/reserveLists/{_id}", tags=["reservation"])
async def delete_food(_id: int, db: Session = Depends(get_db)):
    db_reserve = db.get(Reservation, _id)
    if not db_reserve:
        raise HTTPException(status_code=404, detail="Reservation ID not found.")
    db_reserve.active = False
    db.commit()
    db.refresh(db_reserve)
    return {"message": "Reservation has been deleted succesfully"}


@router.post("/reservations", tags=["reservation"])#, response_model=Dict[str,ReserveSchema])
async def add_reservation(
    request: Request, reservation: CreateReserveSchemaRequest, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(reservation.dict())
    data = reservation.reservation
    logger.info(data.tables[0])
    is_reserved = db.query(Reservation).join(Tables, Reservation.tables).filter(func.date(Reservation.reservedate) == data.reservedate,Tables.name==data.tables[0],Tables.shop==data.shop).first()
    if is_reserved:
        raise HTTPException(status_code=400, detail="Reservation already registered.")
    tables = Tables(name=data.tables[0],reservedate=data.reservedate,shop=data.shop)
    order = Reservation(userId=current_user["id"],username=data.username, phoneno=data.phoneno,reservedate=data.reservedate,reservetime=data.reservetime,
                    description=data.description,status="Pending",active=True,tables=[tables])
    db.add(order)
    db.add(tables)
    db.commit()
    #for eventsource
    #evt_data = json.dumps(parse_obj_as(TablesSchema,tables).dict(), default=str)
    #logger.info(evt_data)
    #db.execute(text("SELECT pg_notify(:channel, :data)").bindparams(channel="match_updates", data=evt_data))
    #db.commit()
    select_id = order.id
    notification = AdminNotiModel(shop=data.shop,title="New Table Request",description=f"{data.tables[0]} Table Booked",status="reserve",select_id=select_id)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    order_dict = parse_obj_as(TablesSchema,tables).dict()
    order_dict["noti"] = "reserve"
    evt_data = json.dumps(order_dict, default=str)
    cursor.execute(f"NOTIFY match_updates, '{evt_data}';")
    ###
    db.refresh(order)
    return {"reservation":order}

@router.get("/reservations/{id}", tags=["reservation"], response_model=Dict[str,ReserveSchema])
def get_reservation_byid(id: int, db: Session = Depends(get_db)):
    reservation = db.get(Reservation, id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation ID not found.")
    return {"reservation":reservation}

@router.delete("/reservations/{id}", tags=["reservation"])
async def delete_reservation(id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    reservations = db.get(Reservation, id)
    if reservations.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Your don't have permission.")
    logger.info(reservations.userId)
    logger.info(current_user["id"])
    db.delete(reservations)
    db.commit()
    return {"message": "User has been deleted succesfully"}

#####
@router.get("/restables", tags=["reservation"], response_model=Dict[str,List[RestableScema]])
async def get_tables(
    reservedate:date = None,shop:str=None,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    if reservedate and shop:
        print
        restables = db.query(Tables).filter(func.date(Tables.reservedate)==reservedate,Tables.shop==shop).order_by(desc(Tables.createdate)).all()
        return {"restable":restables}
    elif not reservedate and shop:
        #from router
        restables = db.query(Tables).filter(func.date(Tables.reservedate)==date.today(),Tables.shop==shop).order_by(desc(Tables.createdate)).all()
        return {"restable":restables}
    else:
        restables = db.query(Tables).filter(func.date(Tables.reservedate)==date.today()).order_by(desc(Tables.createdate)).all()
        return {"restable":restables}

@router.get("/restables/{id}", tags=["reservation"], response_model=Dict[str,RestableScema])
def get_tables_byid(id: int, db: Session = Depends(get_db)):
    restable = db.get(Tables, id)
    if not restable:
        raise HTTPException(status_code=404, detail="Table ID not found.")
    return {"restable":restable}

@router.post("/restables", tags=["reservation"])#, response_model=Dict[str,ReserveSchema])
async def add_tables(
    request: Request, data: CreateTableSchemaRequest, db: Session = Depends(get_db)
):
    logger.info(data.dict())
    tables = data.dict()
    tables["restable"]["id"] = str(uuid4())
    return {"restable":tables["restable"]}


@router.post("/orders", tags=["order"])
async def create_order(
    request: Request, order: CreateOrderSchemaRequest, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    
    data = order.order
    reservation = db.get(Reservation, data.reservation_id)
    logger.info(data)
    cart = db.query(Cart).filter(Cart.id==data.cart_id,Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    logger.info(cart.cart_items)
    if reservation:
        new_order = Order(username=data.username,phone=data.phone,tables=data.tables,reservedate=data.reservedate,payment=data.payment,status="Pending",postImage=data.postImage,description=data.description,user_id=current_user["id"],shop=data.shop,reservation_id=reservation.id)
        reservation.order = new_order
        for cart_item in cart.cart_items:
            logger.info(cart_item)
            order_item = OrderItem(price=cart_item.food.price,quantity=cart_item.quantity,food=cart_item.food,description=cart_item.description)
            new_order.order_items.append(order_item)
            #db.add(order_item)
        cart.status = "CLOSED"
        db.add(new_order)
        db.add(cart)
        db.commit()
        db.refresh(new_order)
        db.refresh(reservation)
    else:
        new_order = Order(username=data.username,phone=data.phone,tables=data.tables,reservedate=data.reservedate,payment=data.payment,status="Pending",postImage=data.postImage,description=data.description,user_id=current_user["id"],shop=data.shop)
        for cart_item in cart.cart_items:
            logger.info(cart_item)
            order_item = OrderItem(price=cart_item.food.price,quantity=cart_item.quantity,food=cart_item.food,description=cart_item.description)
            new_order.order_items.append(order_item)
            #db.add(order_item)
        cart.status = "CLOSED"
        db.add(new_order)
        db.add(cart)
        db.commit()
        db.refresh(new_order)
        

    print("Order ID")
    select_id = new_order.id
    if data.tables=="parcel":
        notification = AdminNotiModel(shop=data.shop,title="New Parcel Request",description=f"{data.username}({data.phone}) parcel {len(cart.cart_items)} items",status="parcel",select_id=select_id)
        db.add(notification)
        db.commit()
        db.refresh(notification)

        order_dict = parse_obj_as(GetReservedOrder,new_order).dict()
        order_dict["noti"] = "parcel"
        order_dict["title"] = f"{data.username}({data.phone})"
        order_dict["item"] = f"parcel {len(cart.cart_items)} items"
        order_dict["reservedate"] =order_dict["createdate"].strftime('%Y-%m-%d %H:%M')
     
        evt_data = json.dumps(order_dict, default=str)
        cursor.execute(f"NOTIFY match_updates, '{evt_data}';")
    return {"order":new_order}
