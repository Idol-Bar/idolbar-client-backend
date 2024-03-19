import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,
    AddToCart,
    AddToCartSchemaRequest,UpdateCartItemDesc
)
from typing import List, Dict
from .database import get_db
from models.model import Cart,CartItem,FoodModel,EndUser,Tables
from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc,Enum
from modules.utils import pagination
from firebase_admin import messaging
router = APIRouter()
auth_handler = AuthToken()

@router.get("/carts", tags=["cart"])#, response_model=FoodCategorySchemaWithMeta)
async def get_carts(
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    user = db.query(EndUser).get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        #raise HTTPException(status_code=404, detail="Open cart not found for this customer")
        return {"cart":[]}
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    cart_item_list = [ {"product_id": item.food_id,"product_name": item.food.name,"quantity": item.quantity,"price":item.food.price} for item in cart_items]

    #return {"cart":cart_items,"meta":{"createdate":cart.reservedate.strftime('%Y-%m-%d'),"tableId":cart.tables}}
    return {"cart":cart_items}
    
@router.post("/carts", tags=["cart"])
async def add_cart(
    request: Request, item: AddToCartSchemaRequest, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(item)
    data = item.cart
    user = db.query(EndUser).get(current_user["id"])
    food = db.query(FoodModel).get(data.food_id)
    restable = db.get(Tables, data.tableId)
    reserve_date = restable.reservation.reservedate
    if not user or not food:
            raise HTTPException(status_code=404, detail="Customer or Product not found")
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        dynamic_date = reserve_date if data.cartype=="reserve" else item.cart.reservedate 
        cart = Cart(user_id=user.id,status="OPEN",reservedate=dynamic_date,tables=item.cart.tableId)
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

@router.get("/carts/{id}", tags=["cart"])
def get_cart_byid(id: int, db: Session = Depends(get_db)):
    cartitem = db.get(CartItem, id)
    if not cartitem:
        raise HTTPException(status_code=404, detail="Cart ID not found.")
    return {"cart":cartitem}

@router.put("/carts/{_id}", tags=["cart"])
async def update_cart(
    _id: int, data: UpdateCartItemDesc,db: Session = Depends(get_db)
):
    cartitem = db.get(CartItem, _id)
    if not cartitem:
        raise HTTPException(status_code=404, detail="Cart ID not found.")
    cartitem.description =  data.cart.description
    db.commit()
    db.refresh(cartitem)
    return {"cart":cartitem}



@router.delete("/carts/{_id}", tags=["cart"])
async def remove_cart(_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = db.query(EndUser).get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        raise HTTPException(status_code=404, detail="Open cart not found for this customer")
    cart_item = db.get(CartItem, _id)
    db.delete(cart_item)
    db.commit()
    return {"message": "CartItem has been deleted succesfully"}

@router.put("/carts/add/{_id}", tags=["cart"])
async def add_cart_item(
    _id: int,db: Session = Depends(get_db),current_user: CurrentUser = Depends(get_current_user)
):
    user = db.query(EndUser).get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        raise HTTPException(status_code=404, detail="Open cart not found for this customer")
    cart_item = db.query(CartItem).get(_id)
    if not cart_item:
            raise HTTPException(status_code=404, detail="Product not found in the cart")
    cart_item.quantity += 1
    db.commit()
    db.refresh(cart_item)
    cart_item.food = db.query(FoodModel).filter(FoodModel.id == cart_item.food_id).first()
    return {"cart":cart_item}


@router.put("/carts/remove/{_id}", tags=["cart"])
async def remove_cart_item(
    _id: int,db: Session = Depends(get_db),current_user: CurrentUser = Depends(get_current_user),
):
    user = db.query(EndUser).get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"], Cart.status == "OPEN").first()
    if not cart:
        raise HTTPException(status_code=404, detail="Open cart not found for this customer")
    cart_item = db.query(CartItem).get(_id)
    if not cart_item:
            raise HTTPException(status_code=404, detail="Product not found in the cart")
    cart_item.quantity -= 1
    db.commit()
    db.refresh(cart_item)
    cart_item.food = db.query(FoodModel).filter(FoodModel.id == cart_item.food_id).first()
    return {"cart":cart_item}