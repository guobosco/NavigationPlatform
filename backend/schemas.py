from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

# 应用分类枚举（Pydantic版）
# 用于数据验证，确保分类是预定义的值之一
class CategoryEnum(str, Enum):
    web = "web"
    desktop = "desktop"
    mobile = "mobile"
    service = "service"
    data = "data"
    other = "other"

# 应用基础模型
# 包含应用共有的字段
class AppBase(BaseModel):
    name: str              # 应用名称
    url: str               # 应用链接
    description: str       # 描述
    developer: str         # 开发者
    deploy_env: str        # 部署环境
    category: CategoryEnum # 分类
    scope: str             # 范围
    admin_contact: str     # 管理员联系方式
    thumbnail_base64: Optional[str] = None # 缩略图 Base64 字符串

# 应用创建模型
# 继承自 AppBase，用于创建应用时的请求体
class AppCreate(AppBase):
    pass

# 待审核应用创建模型
# 用于用户提交应用时的请求体
class PendingAppCreate(AppBase):
    pass

# 应用响应模型
# 用于 API 返回已批准应用的数据结构
class AppResponse(AppBase):
    id: int                # 数据库 ID
    status: Optional[int] = None # 状态
    created_at: datetime   # 创建时间
    
    class Config:
        from_attributes = True # 允许从 ORM 模型创建

# 待审核应用响应模型
# 用于 API 返回待审核应用的数据结构
class PendingAppResponse(AppBase):
    id: int                # 数据库 ID
    submit_token: str      # 提交令牌
    created_at: datetime   # 创建时间

    class Config:
        from_attributes = True

# 系统配置基础模型
# 用于系统配置的读取和更新
class SystemConfigBase(BaseModel):
    title: str  # 系统标题
    slogan: str # 系统标语

# 登录请求模型
# 用于管理员登录请求
class LoginRequest(BaseModel):
    username: str # 用户名
    password: str # 密码

# Token 模型
# 用于登录成功后返回的 JWT Token 结构
class Token(BaseModel):
    access_token: str # 访问令牌
    token_type: str   # 令牌类型（通常为 bearer）
