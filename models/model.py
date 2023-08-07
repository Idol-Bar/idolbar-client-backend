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


class User(Base):
    __tablename__ = "enduser"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, nullable=True)
    birthday = Column(String, nullable=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(ARRAY(JSON), nullable=True)
    info = Column(ARRAY(JSON), nullable=True)
    phoneno = Column(String, unique=True, nullable=False)
    status = Column(String, unique=True, nullable=False)
    active = Column(Boolean, unique=False, default=True)
    tier = relationship("Tier", back_populates="enduser", cascade="all,delete", lazy="dynamic")

class UserInDB(User):
    password: Column(String, nullable=False)


class Tier(Base):
    __tablename__ = "tier"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("enduser.id"))
    enduser = relationship("User", back_populates="tier", cascade="all,delete")
