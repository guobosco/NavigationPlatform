from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    web = "web"
    desktop = "desktop"
    mobile = "mobile"
    service = "service"
    data = "data"
    other = "other"

class AppBase(BaseModel):
    name: str
    url: str
    description: str
    developer: str
    deploy_env: str
    category: CategoryEnum
    scope: str
    admin_contact: str
    thumbnail_base64: Optional[str] = None # Receive as base64 string

class AppCreate(AppBase):
    pass

class PendingAppCreate(AppBase):
    pass

class AppResponse(AppBase):
    id: int
    status: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PendingAppResponse(AppBase):
    id: int
    submit_token: str
    created_at: datetime

    class Config:
        from_attributes = True

class SystemConfigBase(BaseModel):
    title: str
    slogan: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
