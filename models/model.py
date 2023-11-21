from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Float,
    Integer,
    BigInteger,
    String,
    DateTime,
    Date,
    Time,
    ForeignKey,
    JSON,
    ARRAY,
    Boolean,
    BigInteger,
    Enum
)
from handlers.database import Base
import datetime


class BannerModel(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String,nullable=False)
    description = Column(String, nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)

class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String,nullable=False)
    category = Column(String,nullable=False)
    description = Column(String, nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    publishdate = Column(DateTime, default=datetime.datetime.now)
    isnoti = Column(Boolean, unique=False, default=False)
    
class CategoryModel(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String,nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    
class EndUser(Base):
    __tablename__ = "enduser"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=False, nullable=True)
    birthday = Column(String, nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(ARRAY(JSON), nullable=True)
    info = Column(ARRAY(JSON), nullable=True)
    phoneno = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    active = Column(Boolean, unique=False, default=True)
    tier = relationship("Tier", back_populates="enduser", cascade="all,delete", lazy="dynamic")
    code = Column(String,nullable=True)
    state = Column(String,nullable=True)
    division = Column(String,nullable=True)
    #point_id = Column(Integer, ForeignKey('point.id'))
    point = relationship("Point", back_populates="owner")


class Tier(Base):
    __tablename__ = "tier"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("enduser.id"))
    enduser = relationship("EndUser", back_populates="tier", cascade="all,delete")

class TierRule(Base):
    __tablename__ = "tierrule"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String,nullable=False)
    lower = Column(Integer,nullable=False)
    higher = Column(Integer,nullable=False)
    percentage = Column(Integer,nullable=False)
    description = Column(String, nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    unit = Column(Integer, nullable=False,default=1)
    createdate = Column(DateTime, default=datetime.datetime.now)


class Point(Base):
    __tablename__ = 'point'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit = Column(Integer, nullable=False,default=1)
    owner_id = Column(Integer, ForeignKey("enduser.id"))
    owner = relationship("EndUser", uselist=False, back_populates="point")
    transitions = relationship("Transition", back_populates="point")
    expire = Column(DateTime, default=datetime.datetime.now() + datetime.timedelta(days=3))
    createdate = Column(DateTime, default=datetime.datetime.now)

class Transition(Base):
    __tablename__ = 'transitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fromUser = Column(String, nullable=False)
    toUser = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, nullable=False)
    point_id = Column(Integer, ForeignKey('point.id'))
    point = relationship("Point", back_populates="transitions")


class UserInDB(EndUser):
    password: Column(String, nullable=False)


class Money(Base):
    __tablename__ = 'money'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, nullable=False)

class PointLogs(Base):
    __tablename__ = 'pointlogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    point = Column(Integer, nullable=False)
    tier = Column(String, nullable=False)
    username = Column(String, unique=False, nullable=True)
    phoneno = Column(String, unique=False, nullable=True)
    fromUser = Column(String, nullable=True)
    toUser = Column(String, nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, nullable=False)
    info = Column(ARRAY(JSON), nullable=True)


class Reservation(Base):
    __tablename__ = 'reservation'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=False, nullable=True, autoincrement=True)
    phoneno = Column(String, unique=False, nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    reservedate = Column(Date, nullable=False)
    reservetime = Column(Time, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    active = Column(Boolean, unique=False, default=True)
    tables = relationship('Tables', back_populates='reservation', cascade='all, delete-orphan')

class Tables(Base):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False, nullable=True, autoincrement=True)
    shop = Column(String, nullable=False)
    reservation_id = Column(Integer, ForeignKey('reservation.id'))  # Define a foreign key
    reservedate = Column(Date, nullable=False)
    reservation = relationship('Reservation', back_populates='tables')
    createdate = Column(DateTime, default=datetime.datetime.now)


class FoodCategoryModel(Base):
    __tablename__ = "foodcategory"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String,nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    foods = relationship('FoodModel', back_populates='category')

class FoodModel(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String,nullable=False)
    code = Column(String,nullable=False)
    description = Column(String, nullable=False)
    instock = Column(Boolean, unique=False, default=False)
    bestsell = Column(Boolean, unique=False, default=False)
    todayspecial = Column(Boolean, unique=False, default=False)
    discount = Column(Integer, unique=False, default=False)
    price = Column(Integer, unique=False, default=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    category_id = Column(Integer, ForeignKey('foodcategory.id'), nullable=False)
    category = relationship('FoodCategoryModel', back_populates='foods')
    shop = Column(String, nullable=False)

class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    status = Column(String,nullable=False)
    user_id = Column(Integer, ForeignKey("enduser.id"))
    #enduser = relationship("EndUser", back_populates="cart", cascade="all,delete")
    cart_items = relationship('CartItem', back_populates='cart')

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False, autoincrement=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    food_id = Column(Integer, ForeignKey('foods.id'))
    food = relationship('FoodModel')
    cart_id = Column(Integer, ForeignKey('carts.id'))
    cart = relationship('Cart', back_populates='cart_items')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    payment = Column(String,nullable=False)
    status = Column(String,nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("enduser.id"))
    enduser = relationship("EndUser")
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    food_id = Column(Integer, ForeignKey('foods.id'))
    food = relationship('FoodModel')
    order_id = Column(Integer, ForeignKey('orders.id'))
    order = relationship('Order', back_populates='order_items')

   
class NotiModel(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    description = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)

class FaqModel(Base):
    __tablename__ = "faq"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(String,nullable=False)
    answer = Column(String,nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)


class EventModel(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=True)
    reservedate = Column(Date, nullable=False)
    postImage = Column(ARRAY(JSON), nullable=True)
    description = Column(String, nullable=False)
    status = Column(String,nullable=True)
    active = Column(Boolean, unique=False, default=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
