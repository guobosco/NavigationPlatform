from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime, ForeignKey, Enum, SmallInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

try:
    from .database import Base
except ImportError:
    from database import Base

# 应用状态枚举
class AppStatus(int, enum.Enum):
    pending = 0  # 待审核
    online = 1   # 已上线
    rejected = 2 # 已拒绝
    offline = 3  # 已下线

# 用户角色枚举
class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    plain_password = Column(String, nullable=True) # 仅用于管理员查看（不推荐生产环境使用）
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    apps = relationship("App", back_populates="owner")
    credentials = relationship("AppCredential", back_populates="user")

# 应用分类模型 (保留类名，修改注释)
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    label = Column(String) # 显示名称
    sort_order = Column(Integer, default=0)

# 应用范围模型 (保留类名，修改注释)
class AppScope(Base):
    __tablename__ = "app_scopes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    label = Column(String) # 显示名称
    sort_order = Column(Integer, default=0)

# 统一的应用模型 (保留类名，修改注释为系统)
class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    description = Column(Text)
    developer = Column(String)
    server_location = Column(String) # 服务器部署位置
    
    # 外键关联
    category_id = Column(Integer, ForeignKey("categories.id"))
    scope_id = Column(Integer, ForeignKey("app_scopes.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True) # 允许为空（匿名提交或系统预设）
    
    admin_contact = Column(String)
    contact_info = Column(String, nullable=True) # 管理员联系方式
    thumbnail = Column(LargeBinary, nullable=True)
    
    status = Column(SmallInteger, default=AppStatus.pending.value)
    reject_reason = Column(Text, nullable=True) # 拒绝原因
    
    # 排序和标记
    sort_order = Column(Integer, default=0) # 排序权重，越大越靠前
    is_pinned = Column(Boolean, default=False) # 是否置顶
    is_starred = Column(Boolean, default=False) # 是否标星
    
    visits = Column(Integer, default=0) # 访问量
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="apps")
    category = relationship("Category")
    scope = relationship("AppScope")
    credentials = relationship("AppCredential", back_populates="app")

# 用户密码管理模型
class AppCredential(Base):
    __tablename__ = "app_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    app_id = Column(Integer, ForeignKey("apps.id"))
    
    username_text = Column(String) # 备注的用户名
    password_text = Column(String) # 备注的密码（明文或简单加密，按需求文本体现）
    note = Column(Text, nullable=True) # 备注
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="credentials")
    app = relationship("App", back_populates="credentials")

# 系统配置模型
class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True, index=True)
    value = Column(String)

# 审计日志模型
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    action = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
