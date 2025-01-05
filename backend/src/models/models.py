from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey, Float
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
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String,  nullable=False)


class Organization(Timestamp, Base):
    __tablename__ = "organizations"

    organization_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, nullable=False, unique=True)


class UserOrganization(Timestamp, Base):
    __tablename__ = "user_organizations"

    user_organization_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    role = Column(Integer, nullable=False)


class Cluster(Timestamp, Base):
    __tablename__ = "clusters"

    cluster_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    total_ram = Column(Integer, nullable=False)
    total_cpu = Column(Integer, nullable=False)
    total_gpu = Column(Integer, nullable=False)
    available_ram = Column(Integer, nullable=False)
    available_cpu = Column(Integer, nullable=False)
    available_gpu = Column(Integer, nullable=False)
    

class Deployment(Base):
    __tablename__ = "deployments"

    deployment_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.cluster_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    docker_image_path = Column(String, nullable=False)
    required_ram = Column(Integer, nullable=False)
    required_cpu = Column(Integer, nullable=False)
    required_gpu = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)