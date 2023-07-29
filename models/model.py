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
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(ARRAY(JSON), nullable=True)
    active = Column(Boolean, unique=False, default=True)
    role = relationship("Role", back_populates="user", cascade="all,delete", lazy="dynamic")

class UserInDB(User):
    password: Column(String, nullable=False)


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="role", cascade="all,delete")
