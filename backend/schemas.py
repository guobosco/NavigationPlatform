from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- Enums ---
class UserRole(str, Enum):
    """用户角色枚举"""
    admin = "admin" # 管理员
    user = "user"   # 普通用户

class AppStatus(int, Enum):
    """应用状态枚举"""
    pending = 0  # 待审核
    online = 1   # 已上线
    rejected = 2 # 已拒绝
    offline = 3  # 已下线

# --- User Schemas ---
class UserBase(BaseModel):
    """用户基础模型"""
    username: str

class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    role: UserRole = UserRole.user

class User(UserBase):
    """用户响应模型"""
    id: int
    role: UserRole
    created_at: datetime
    plain_password: Optional[str] = None # Admin only

    class Config:
        from_attributes = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str
    label: str
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    """分类响应模型"""
    id: int

    class Config:
        from_attributes = True

# --- AppScope Schemas ---
class AppScopeBase(BaseModel):
    """应用范围基础模型"""
    name: str
    label: str
    sort_order: int = 0

class AppScopeCreate(AppScopeBase):
    pass

class AppScope(AppScopeBase):
    """应用范围响应模型"""
    id: int

    class Config:
        from_attributes = True

# --- App Schemas ---
class AppBase(BaseModel):
    """应用基础模型"""
    name: str
    url: str
    description: str
    category_id: int
    scope_id: int
    developer: str
    admin_contact: str
    contact_info: Optional[str] = None
    server_location: str = "默认位置"
    thumbnail_base64: Optional[str] = None

class AppCreate(AppBase):
    """应用创建模型"""
    pass

class AppUpdate(BaseModel):
    """应用更新模型"""
    status: Optional[AppStatus] = None
    reject_reason: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    # ... other fields as needed

class AppResponse(AppBase):
    """应用响应模型"""
    id: int
    status: AppStatus
    reject_reason: Optional[str] = None
    owner_id: Optional[int] = None
    thumbnail_base64: Optional[str] = None
    visits: int = 0
    created_at: datetime
    
    # 嵌套对象以便前端显示 Label
    category_label: Optional[str] = None 
    scope_label: Optional[str] = None
    contact_info: Optional[str] = None

    # New Fields
    sort_order: int = 0
    is_pinned: bool = False
    is_starred: bool = False
    visits: int = 0
    
    class Config:
        from_attributes = True

# --- App Admin Update Schema ---
class AppAttributeUpdate(BaseModel):
    sort_order: Optional[int] = None
    is_pinned: Optional[bool] = None
    is_starred: Optional[bool] = None

class AppAdminDetailUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    developer: Optional[str] = None
    server_location: Optional[str] = None
    admin_contact: Optional[str] = None
    contact_info: Optional[str] = None
    category_id: Optional[int] = None
    scope_id: Optional[int] = None

# --- Credential Schemas ---
class CredentialBase(BaseModel):
    """凭据基础模型"""
    app_id: int
    username_text: str
    password_text: str
    note: Optional[str] = None

class CredentialCreate(CredentialBase):
    pass

class CredentialResponse(CredentialBase):
    """凭据响应模型"""
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# --- System Config Schemas ---
class SystemConfigBase(BaseModel):
    """系统配置模型"""
    title: str
    slogan: str
    home_nav_title: str = "系统导航"
    footer_copyright: str = "© 2024 StarBase. All rights reserved."
    nav_publish_text: str = "发布"
    submit_page_title: str = "发布新系统"
    submit_page_desc: str = "填写下方信息提交您的系统，管理员审核通过后将展示在首页"
    
    # Placeholders
    placeholder_name: str = "例如：协同办公系统"
    placeholder_url: str = "http://example.com"
    placeholder_desc: str = "简要描述系统的主要功能和用途..."
    placeholder_developer: str = "开发团队或个人姓名"
    placeholder_admin_name: str = "系统管理员姓名"
    placeholder_contact_info: str = "手机号或邮箱地址"
    placeholder_server_location: str = "例如：总部机房 / 阿里云"

# --- Auth Schemas ---
class Token(BaseModel):
    """JWT 令牌模型"""
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    """令牌数据载荷"""
    username: Optional[str] = None
