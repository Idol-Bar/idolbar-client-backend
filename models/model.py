from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Float,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    JSON,
    ARRAY,
    Boolean,
    BigInteger
)
from handlers.database import Base
import datetime



class EndUser(Base):
    __tablename__ = "enduser"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, nullable=True)
    birthday = Column(String, nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(ARRAY(JSON), nullable=True)
    info = Column(ARRAY(JSON), nullable=True)
    phoneno = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    active = Column(Boolean, unique=False, default=True)
    tier = relationship("Tier", back_populates="enduser", cascade="all,delete", lazy="dynamic")
    #point_id = Column(Integer, ForeignKey('point.id'))
    point = relationship("Point", back_populates="owner")


class Tier(Base):
    __tablename__ = "tier"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("enduser.id"))
    enduser = relationship("EndUser", back_populates="tier", cascade="all,delete")


class Point(Base):
    __tablename__ = 'point'
    id = Column(Integer, primary_key=True)
    unit = Column(Integer, nullable=False,default=1)
    owner_id = Column(Integer, ForeignKey("enduser.id"))
    owner = relationship("EndUser", uselist=False, back_populates="point")
    transitions = relationship("Transition", back_populates="point")
    expire = Column(DateTime, default=datetime.datetime.now() + datetime.timedelta(days=3))
    createdate = Column(DateTime, default=datetime.datetime.now)

class Transition(Base):
    __tablename__ = 'transitions'
    id = Column(Integer, primary_key=True)
    fromUser = Column(String, nullable=False)
    toUser = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, nullable=False)
    point_id = Column(Integer, ForeignKey('point.id'))
    point = relationship("Point", back_populates="transitions")


class UserInDB(EndUser):
    password: Column(String, nullable=False)

