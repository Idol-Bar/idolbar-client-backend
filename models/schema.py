from datetime import datetime, date,time
from uuid import uuid4, UUID
from typing import List, Optional, Any
from pydantic import BaseModel, validator,Field
from sqlalchemy.orm import Query
import json
import uuid
class OrmBase(BaseModel):
    id: int

    @validator("*", pre=True)
    def evaluate_lazy_columns(cls, v):
        if isinstance(v, Query):
            return v.all()
        return v

    class Config:
        orm_mode = True


class MetaSchema(OrmBase):
    id: Optional[int] =  1
    total_pages: int
    page: Optional[int] =  1


class RoleSchema(OrmBase):
    name: str


class UserSchema(OrmBase):
    email: str
    username: str
    createdate: datetime
    role: List[RoleSchema]


class NewUserSchema(BaseModel):
    email: str
    username: str
    password: str
    role: str


class CurrentUser(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True

###SMS POOH
class PhoneVerifySchema(BaseModel):
    phone: str
    code: str

    class Config:
        orm_mode = True

class PhoneRegisterSchema(BaseModel):
    phone: str

    class Config:
        orm_mode = True


class LoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True

class PhoneLoginSchema(BaseModel):
    verificationID: str
    code: str

    class Config:
        orm_mode = True

class RegisterPhoneSchema(BaseModel):
    username: str
    birthday: str
    state: str
    division: str
    shop:str
    postImage: Optional[List] = []
    gender: Optional[str] = "male"
    class Config:
        orm_mode = True

class RegisterPhoneSchemaRequest(BaseModel):
    phoneRegister: RegisterPhoneSchema

class TierSchema(BaseModel):
    name: str


class ProfileSchema(BaseModel):
    id:int
    username: str
    birthday: str
    postImage: Optional[List] = []
    phoneno: str
    createdate: datetime
    code: Optional[str] = ""
    tier: List[TierSchema]
    unit:int
    class Config:
        orm_mode = True
##Point Schema

class PayPointSchema(OrmBase):
    id: Optional[int]
    unit: int

    class Config:
        orm_mode = True

class SharePointSchema(OrmBase):
    id: Optional[int]
    userId: int
    unit: int

    class Config:
        orm_mode = True

class SharePointWithPhonSchema(BaseModel):
    phoneno: str
    unit: int

    class Config:
        orm_mode = True

### Reservation
"""
class TablesSchema(OrmBase):
    name: str
    reservedate: date
    createdate: datetime
    reservation_id:int

class ReserveSchema(OrmBase):
    username: str
    phoneno: str
    createdate: datetime
    reservedate: date
    reservetime: time
    description: str
    status: bool
    active: Optional[bool] = False
    tables: List[TablesSchema]  = []

    class Config:
        orm_mode = True

class CreateReserveSchema(OrmBase):
    id: Optional[int]
    # username: str
    # phoneno: str
    shop: str
    reservedate: date
    reservetime: time
    description: str
    status: Optional[bool] = True
    active: Optional[bool] = True
    tables: List

    class Config:
        orm_mode = True

class CreateReserveSchemaRequest(BaseModel):
    reservation: CreateReserveSchema """

class GetAppCategorySchema(OrmBase):
    id: int
    name: str
    postImage: Optional[List] = []
    createdate: datetime
    class Config:
        orm_mode = True


class GetAppPostSchema(OrmBase):
    id: Optional[int]
    category: str
    title: str
    shop: str
    description: str
    createdate: datetime
    publishdate: datetime
    postImage: Optional[List] = []
    class Config:
        orm_mode = True


###Food Category
class GetFoodCategorySchema(OrmBase):
    id: int
    name: str
    shop: Optional[str] = ""
    postImage: Optional[List] = []
    createdate: datetime
    class Config:
        orm_mode = True

class FoodCategorySchemaWithMeta(BaseModel):
    foodCategory: List[GetFoodCategorySchema] = []
    meta : MetaSchema

class GetFoodSchema(OrmBase):
    id: Optional[int]
    name: str
    code: str
    description: str
    instock: bool
    bestsell: bool
    todayspecial: bool
    discount: int
    price: int
    createdate: datetime
    postImage: Optional[List] = []
    category: GetFoodCategorySchema  = []
    shop: Optional[str] = "shop1"

    class Config:
        orm_mode = True

class FoodSchemaWithMeta(BaseModel):
    food: List[GetFoodSchema] = []
    meta : MetaSchema


##Cart 
class AddToCart(BaseModel):
    food_id: int
    quantity: int
    reservedate: date
    tableId:str
    cartype: Optional[str] = ""
    class Config:
        orm_mode = True

class AddToCartSchemaRequest(BaseModel):
    cart: AddToCart

class DescCart(BaseModel):
    description: str

    class Config:
        orm_mode = True

class UpdateCartItemDesc(BaseModel):
    cart: DescCart

class CartList(BaseModel):
    price:int
    quantity:int
    cart_id:int
    createdate: datetime
    food_id:int
    food: GetFoodSchema

##
class CreateOrder(BaseModel):
    reservation_id:Optional[int]
    cart_id: int
    payment: str
    description: Optional[str]= ""
    shop: Optional[str]= "shop1"
    postImage: Optional[List] = []
    reservedate:date
    username:str
    tables:str
    phone:str
    @validator("shop")
    def check_shop(cls, v):
        if v not in ["shop1", "shop2"]:
            raise ValueError("Has to be Shop1 or Shop2")
        return v

class CreateOrderSchemaRequest(BaseModel):
    order: CreateOrder

class OrderItemSchema(BaseModel):
    id: Optional[int]
    price:Optional[int]=0
    food_id: Optional[int]=0
    quantity: Optional[int]=0
    food: GetFoodSchema
    description: Optional[str] = ""

    class Config:
        orm_mode = True

class GetOrder(BaseModel):
    id: Optional[int]
    createdate: datetime
    payment: str
    postImage: Optional[List] = []
    user_id: int
    status: str
    description: str
    order_items: Optional[List[OrderItemSchema]] = None
    shop: Optional[str] = "shop1"
    class Config:
        orm_mode = True

class GetReservedOrder(BaseModel):
    id: Optional[int]
    createdate: datetime
    payment: str
    postImage: Optional[List] = []
    user_id: int
    status: str
    description: str
    order_items: Optional[List[OrderItemSchema]] = None
    shop: Optional[str] = "shop1"
    class Config:
        orm_mode = True

class GetOrderSchemaWithMeta(BaseModel):
    order: List[GetOrder] = []
    meta : MetaSchema

class EventSchema(BaseModel):
    id: Optional[int]
    name: str
    shop: str
    description: str
    reservedate: date
    postImage: Optional[List] = []

    class Config:
        orm_mode = True



##Payment 

class PaymentSchema(BaseModel):
    id: Optional[int]
    name: str
    account: str
    shop: Optional[str] = "shop1"
    createdate: date
    #postImage: Optional[List] = []

    class Config:
        orm_mode = True

class CreateAppReviewSchema(OrmBase):
    id: Optional[int]
    title: str
    description: str
    status:Optional[str]="PENDING"
    postImage: Optional[List] = []
    owner:Optional[str]="USER"
    class Config:
        orm_mode = True

class CreateAppReviewSchemaRequest(BaseModel):
    review: CreateAppReviewSchema

class GetReviewSchema(OrmBase):
    id: int
    title: str
    description: str
    postImage: Optional[List] = []
    createdate: datetime
    class Config:
        orm_mode = True


### Reservation
class CreateTableSchema(OrmBase):
    id: Optional[int]
    name: str
    reservedate: date

class CreateTableSchemaRequest(BaseModel):
    restable: CreateTableSchema

class TablesSchema(OrmBase):
    name: str
    shop:Optional[str] = ""
    reservedate: date
    createdate: datetime
    reservation_id:int



class ReserveSchema(OrmBase):
    username: str
    phoneno: str
    createdate: datetime
    reservedate: date
    reservetime: time
    description: str
    status: str
    active: Optional[bool] = False
    tables: List[TablesSchema]  = []
    orders: Optional[List[GetOrder]] = None
    class Config:
        orm_mode = True

class EmptyReservationResponse(BaseModel):
    reservation: Optional[ReserveSchema]


class ReservationSchema(OrmBase):
    userId:Optional[int] = 0
    username: str
    phoneno: str
    createdate: datetime
    reservedate: date
    reservetime: time
    description: str
    status: str
    active: Optional[bool] = False
    tables: List[TablesSchema]  = []

    class Config:
        orm_mode = True

class RestableScema(OrmBase):
    name: str
    shop: str
    reservedate: date
    createdate: datetime
    reservation_id:int
    reservation:ReservationSchema

class ReserveSchemaWithMeta(BaseModel):
    reserveList: List[ReserveSchema] = []
    meta : MetaSchema

class CreateReserveSchema(OrmBase):
    id: Optional[int]
    username: str
    phoneno: str
    shop: str
    reservedate: date
    reservetime: time
    description: str
    status: Optional[bool] = True
    active: Optional[bool] = True
    tables: List

    class Config:
        orm_mode = True

class CreateReserveSchemaRequest(BaseModel):
    reservation: CreateReserveSchema