from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_mixin

from src.core.dbutils import Base

@declarative_mixin
class Timestamp:
    created_at = Column(DateTime, default=func.now(), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Timestamp, Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False unique=True, index=True)
    password = Column(String,  nullable=False)


class Organization(Base):
    __tablename__ = "organizations"
    organization_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, nullable=False, unique=True)


class UserOrganization(Base):
    __tablename__ = "user_organizations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, ForeignKey("users.user_id"))
    organization_id = Column(Integer, nullable=False, ForeignKey("organizations.organization_id"))