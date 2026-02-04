from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime, Enum, SmallInteger
from sqlalchemy.sql import func
import enum
from .database import Base

class CategoryEnum(str, enum.Enum):
    web = "web"
    desktop = "desktop"
    mobile = "mobile"
    service = "service"
    data = "data"
    other = "other"

class AppStatus(int, enum.Enum):
    pending = 0
    online = 1
    offline = 2

class ApprovedApp(Base):
    __tablename__ = "approved_apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    description = Column(Text)
    developer = Column(String)
    deploy_env = Column(String)
    category = Column(Enum(CategoryEnum))
    scope = Column(String)
    admin_contact = Column(String)
    thumbnail = Column(LargeBinary, nullable=True) # Max 100KB checked by frontend
    status = Column(SmallInteger, default=AppStatus.online.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PendingApp(Base):
    __tablename__ = "pending_apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    description = Column(Text)
    developer = Column(String)
    deploy_env = Column(String)
    category = Column(Enum(CategoryEnum))
    scope = Column(String)
    admin_contact = Column(String)
    thumbnail = Column(LargeBinary, nullable=True)
    submit_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    action = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
