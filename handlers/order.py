import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    AddToCart,
 
)
from typing import List, Dict
from .database import get_db
from models.model import Cart,CartItem,FoodModel,EndUser
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc,Enum
from modules.utils import pagination
from firebase_admin import messaging
router = APIRouter()
auth_handler = AuthToken()

    
@router.post("/orders", tags=["order"])
async def create_order(
    request: Request, data: AddToCart, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(data)
    user = db.query(EndUser).get(current_user["id"])
    food = db.query(FoodModel).get(data.food_id)
    if not user or not food:
            raise HTTPException(status_code=404, detail="Customer or Product not found")
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        cart = Cart(user_id=user.id,status="OPEN")
        db.add(cart)
        db.commit()
    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.food_id == data.food_id).first()
    if cart_item:
        cart_item.quantity += data.quantity
    else:
        cart_item = CartItem(cart_id=cart.id, food_id=data.food_id, quantity=data.quantity)
        db.add(cart_item)
    db.commit()
    return {"cart":data}