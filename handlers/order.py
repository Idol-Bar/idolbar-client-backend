import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    CreateOrder,
    GetOrder,
    GetOrderSchemaWithMeta
 
)
from typing import List, Dict
from .database import get_db
from models.model import Cart,CartItem,FoodModel,EndUser,Order,OrderItem
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc,Enum
from modules.utils import pagination
from firebase_admin import messaging
router = APIRouter()
auth_handler = AuthToken()


@router.get("/orders", tags=["order"],response_model=GetOrderSchemaWithMeta)#, response_model=Dict[str,List[GetOrder]])
async def get_orders(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(Order).count()
    meta_data =  pagination(page,per_page,count)
    order_data = db.query(Order).order_by(desc(Order.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"order":order_data,"meta":meta_data}


@router.post("/orders", tags=["order"])
async def create_order(
    request: Request, data: CreateOrder, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    current_user= {"id":1}
    logger.info(data)
    cart = db.query(Cart).filter(Cart.id==data.cart_id,Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    logger.info(cart.cart_items)
    new_order = Order(payment=data.payment,status="Pending",postImage=data.postImage,description=data.description,user_id=current_user["id"])
    for cart_item in cart.cart_items:
        logger.info(cart_item)
        order_item = OrderItem(price=cart_item.food.price,quantity=cart_item.quantity,food=cart_item.food)
        new_order.order_items.append(order_item)
        #db.add(order_item)
    cart.status = "CLOSED"
    db.add(new_order)
    db.add(cart)
    db.commit()
    db.refresh(new_order)
    return {"order":new_order}

@router.get("/orders/{id}", tags=["order"], response_model=Dict[str,GetOrder])
def get_order_byid(id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    order = db.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order ID not found.")
    return {"order":order}